"""Stake views: top-up, reclaim, and participant history."""

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.idempotency import IdempotencyKeyMixin
from recommendations.models import Recommendation
from recommendations.pagination import RecommendationPagination
from recommendations.serializers import (
    RecommendationEnvelopeSerializer,
    RecommenderParticipantSerializer,
    StakeAddSerializer,
)
from recommendations.throttles import (
    RecommendationReadThrottle,
    RecommendationStakeThrottle,
)
from recommendations.views.core import activation_hints


class StakeBaseView(APIView):
    """POST top-up / DELETE reclaim for the caller's recommender stake.

    Both operations lock the parent recommendation row with
    ``select_for_update()`` and only mutate the caller's
    ``RecommenderParticipant`` locked balance. Lifecycle state (``is_active``
    for top-ups, ``Recommendation.status``, ``current_recommender``,
    ``recommendation_cycle_number``) is never changed here — positions are
    opened exclusively through recommend/reactivate (Plan 0018).
    """

    def _locked_recommendation(self, id):
        return get_object_or_404(Recommendation.objects.select_for_update(), id=id)

    @extend_schema(
        summary="Reclaim recommender stake",
        description=(
            "Authenticated only. Reclaims all locked SOL from the caller's "
            "active recommender position: sets locked_amount_lamports to 0, "
            "records reclaimed_at, and deactivates the position. Does not "
            "change recommendation lifecycle state. Returns Solana hints."
        ),
        responses={
            200: RecommendationEnvelopeSerializer,
            400: OpenApiResponse(description="No active stake to reclaim."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
        },
    )
    def delete(self, request, id):
        with transaction.atomic():
            recommendation = self._locked_recommendation(id)
            participant = (
                recommendation.recommender_participants.filter(
                    account=request.user, is_active=True
                )
                .order_by("-reactivation_number", "-created_at")
                .first()
            )
            if participant is None:
                return Response(
                    {
                        "detail": _(
                            "You do not have an active stake on this recommendation."
                        )
                    },
                    status=400,
                )
            reclaimed_amount = participant.locked_amount_lamports
            now = timezone.now()
            participant.locked_amount_lamports = 0
            participant.reclaimed_at = now
            participant.last_stake_change_at = now
            participant.is_active = False
            participant.save(
                update_fields=[
                    "locked_amount_lamports",
                    "reclaimed_at",
                    "last_stake_change_at",
                    "is_active",
                    "updated_at",
                ]
            )
            # current_recommender means "account currently staked on the
            # active cycle; null when inactive" (decision 0011). The reclaimed
            # participant is now inactive, so stop advertising it as current.
            if recommendation.current_recommender_id == participant.account_id:
                recommendation.current_recommender = None
                recommendation.save(update_fields=["current_recommender", "updated_at"])
        return Response(
            RecommendationEnvelopeSerializer(
                instance={
                    "recommendation": recommendation,
                    "recommender_participant": RecommenderParticipantSerializer(
                        participant
                    ).data,
                    "solana_hints": activation_hints(
                        recommendation, reclaimed_amount, request.user
                    ),
                }
            ).data
        )

    def post(self, request, id):
        with transaction.atomic():
            recommendation = self._locked_recommendation(id)
            participant = (
                recommendation.recommender_participants.filter(
                    account=request.user, is_active=True
                )
                .order_by("-reactivation_number", "-created_at")
                .first()
            )
            if participant is None:
                return Response(
                    {
                        "detail": _(
                            "You need an existing stake position on this "
                            "recommendation. Use recommend or reactivate to "
                            "open one."
                        )
                    },
                    status=400,
                )
            serializer = StakeAddSerializer(
                data=request.data,
                context={
                    "existing_locked_lamports": participant.locked_amount_lamports
                },
            )
            serializer.is_valid(raise_exception=True)
            amount_lamports = serializer.validated_data["amount_lamports"]
            participant.locked_amount_lamports += amount_lamports
            participant.last_stake_change_at = timezone.now()
            participant.save(
                update_fields=[
                    "locked_amount_lamports",
                    "last_stake_change_at",
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
        summary="Add recommender stake",
        description=(
            "Authenticated only. Top-up only: requires an existing "
            "RecommenderParticipant for the caller (400 otherwise). Adds at "
            "least 50,000,000 lamports while keeping the total at 0 or at "
            "least 0.2 SOL, and never changes lifecycle state. Idempotent "
            "when an Idempotency-Key header is supplied. Returns Solana hints."
        ),
        request=StakeAddSerializer,
        responses={
            200: RecommendationEnvelopeSerializer,
            400: OpenApiResponse(
                description="No existing position, below minimum, or dust balance."
            ),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
            409: OpenApiResponse(description="Idempotency key already in use."),
        },
    ),
)
class StakeView(IdempotencyKeyMixin, StakeBaseView):
    """POST /api/recommendations/{id}/stake/ — top up stake; DELETE reclaims.

    The explicit ``@extend_schema_view(post=...)`` is required: the
    ``IdempotencyKeyMixin`` sits first in the MRO and shadows
    ``StakeBaseView.post`` from drf-spectacular. DELETE is not idempotency-
    keyed per the plan's endpoint catalog.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationStakeThrottle]


class StakeHistoryView(APIView):
    """GET /api/recommendations/{id}/stake/history/ — participant history."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List recommender stake history",
        description=(
            "Public endpoint. Returns paginated RecommenderParticipant "
            "history for the recommendation ordered by reactivation number."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Paginated list of recommender participants."
            ),
            404: OpenApiResponse(description="Recommendation not found."),
        },
    )
    def get(self, request, id):
        recommendation = get_object_or_404(Recommendation, id=id)
        queryset = recommendation.recommender_participants.order_by(
            "reactivation_number"
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            RecommenderParticipantSerializer(page, many=True).data
        )
