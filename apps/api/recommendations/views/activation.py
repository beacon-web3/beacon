"""Activation views: recommend (first activation) and reactivate (later cycles)."""

from django.db import IntegrityError, transaction
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.idempotency import IdempotencyKeyMixin
from recommendations.models import Recommendation, RecommenderParticipant
from recommendations.serializers import (
    ReactivateSerializer,
    RecommendationEnvelopeSerializer,
    RecommenderParticipantSerializer,
    RecommendSerializer,
)
from recommendations.throttles import RecommendationActThrottle
from recommendations.views.core import activation_hints


class ActivationBaseView(APIView):
    """Shared POST logic for recommend and reactivate.

    Both endpoints lock the recommendation row, re-check lifecycle state, and
    create a new active RecommenderParticipant. They differ only in the
    participant's reactivation number and the already-active-participant guard.
    """

    action = None
    serializer_class = None

    def post(self, request, id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount_lamports = serializer.validated_data["amount_lamports"]
        with transaction.atomic():
            recommendation = get_object_or_404(
                Recommendation.objects.select_for_update(), id=id
            )
            if recommendation.status == Recommendation.Status.ACTIVE:
                return Response(
                    {"detail": _("This recommendation is already active.")}, status=400
                )
            if self.action == "recommend":
                if recommendation.recommendation_cycle_number > 0:
                    return Response(
                        {"detail": _("Use the reactivate endpoint for later cycles.")},
                        status=400,
                    )
                if recommendation.recommender_participants.filter(
                    account=request.user, is_active=True
                ).exists():
                    return Response(
                        {
                            "detail": _(
                                "You already have an active recommendation stake "
                                "on this recommendation."
                            )
                        },
                        status=400,
                    )
                reactivation_number = 0
            else:  # reactivate
                if recommendation.recommendation_cycle_number == 0:
                    return Response(
                        {
                            "detail": _(
                                "Use the recommend endpoint for first activation."
                            )
                        },
                        status=400,
                    )
                reactivation_number = (
                    recommendation.recommender_participants.aggregate(
                        Max("reactivation_number")
                    )["reactivation_number__max"]
                    or 0
                ) + 1
            now = timezone.now()
            try:
                participant = RecommenderParticipant.objects.create(
                    account=request.user,
                    recommendation=recommendation,
                    locked_amount_lamports=amount_lamports,
                    initial_lock_at=now,
                    is_active=True,
                    reactivation_number=reactivation_number,
                )
            except IntegrityError:
                # A different user slipped an active participant past the
                # guards (partial unique constraint on one active participant
                # per recommendation); fail cleanly instead of a 500.
                return Response(
                    {
                        "detail": _(
                            "This recommendation already has an active "
                            "recommender participant."
                        )
                    },
                    status=400,
                )
            recommendation.status = Recommendation.Status.ACTIVE
            recommendation.current_recommender = request.user
            recommendation.recommendation_cycle_number += 1
            recommendation.activated_at = now
            recommendation.deactivated_at = None
            # auto_now fields only persist when listed in update_fields.
            recommendation.save(
                update_fields=[
                    "status",
                    "current_recommender",
                    "recommendation_cycle_number",
                    "activated_at",
                    "deactivated_at",
                    "updated_at",
                ]
            )
        return Response(
            RecommendationEnvelopeSerializer(
                instance={
                    "recommendation": recommendation,
                    "recommender_participant": RecommenderParticipantSerializer(
                        participant
                    ).data,
                    "solana_hints": activation_hints(
                        recommendation, amount_lamports, request.user
                    ),
                }
            ).data
        )


@extend_schema_view(
    post=extend_schema(
        summary="Recommend a book",
        description=(
            "Authenticated only. Locks a curator stake and activates an "
            "INACTIVE recommendation; idempotent when an Idempotency-Key "
            "header is supplied."
        ),
        request=RecommendSerializer,
        responses={
            200: RecommendationEnvelopeSerializer,
            400: OpenApiResponse(description="Already active or invalid input."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
            409: OpenApiResponse(description="Idempotency key already in use."),
        },
    ),
)
class RecommendView(IdempotencyKeyMixin, ActivationBaseView):
    """POST /api/recommendations/{id}/recommend/ — activate a recommendation."""

    action = "recommend"
    serializer_class = RecommendSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationActThrottle]


@extend_schema_view(
    post=extend_schema(
        summary="Reactivate a recommendation",
        description=(
            "Authenticated only. Re-activates an INACTIVE recommendation that "
            "has been active before; idempotent when an Idempotency-Key header "
            "is supplied."
        ),
        request=ReactivateSerializer,
        responses={
            200: RecommendationEnvelopeSerializer,
            400: OpenApiResponse(description="Already active or invalid input."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
            409: OpenApiResponse(description="Idempotency key already in use."),
        },
    ),
)
class ReactivateView(IdempotencyKeyMixin, ActivationBaseView):
    """POST /api/recommendations/{id}/reactivate/ — reactivate a recommendation."""

    action = "reactivate"
    serializer_class = ReactivateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationActThrottle]
