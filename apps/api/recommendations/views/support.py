"""Support views: quote preparation, confirmation, and supporter listing."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Max
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
from recommendations.models import SUPPORT_AMOUNT_LAMPORTS, Recommendation, Support
from recommendations.pagination import RecommendationPagination
from recommendations.serializers import (
    SupportConfirmSerializer,
    SupportCreateSerializer,
    SupportEnvelopeSerializer,
    SupportPrepareEnvelopeSerializer,
    SupportReadSerializer,
)
from recommendations.throttles import (
    RecommendationReadThrottle,
    RecommendationSupportThrottle,
)
from recommendations.views.core import support_hints


class SupportView(APIView):
    """POST /api/recommendations/{id}/support/ — prepare support (quote only).

    Performs no database writes: returns the anticipated next supporter
    number, fixed support amount, current cycle number, and Solana hints so
    the client can build and sign the support transaction.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationSupportThrottle]

    @extend_schema(
        summary="Prepare a support transaction",
        description=(
            "Authenticated only. Returns a support quote (next supporter "
            "number, fixed amount, cycle number) and Solana hints. No writes."
        ),
        request=SupportCreateSerializer,
        responses={
            200: SupportPrepareEnvelopeSerializer,
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
            409: OpenApiResponse(
                description="You already support this recommendation."
            ),
        },
    )
    def post(self, request, id):
        recommendation = get_object_or_404(Recommendation, id=id)
        if Support.objects.filter(
            supporter=request.user, recommendation=recommendation
        ).exists():
            return Response(
                {"detail": _("You already support this recommendation.")}, status=409
            )
        supporter_number = (
            recommendation.supports.aggregate(Max("supporter_number"))[
                "supporter_number__max"
            ]
            or 0
        ) + 1
        return Response(
            SupportPrepareEnvelopeSerializer(
                instance={
                    "support_quote": {
                        "supporter_number": supporter_number,
                        "amount_lamports": SUPPORT_AMOUNT_LAMPORTS,
                        "recommendation_cycle_number": (
                            recommendation.recommendation_cycle_number
                        ),
                    },
                    "solana_hints": support_hints(recommendation, supporter_number),
                }
            ).data
        )


class SupportConfirmBaseView(APIView):
    """Shared POST logic for confirming a support payment."""

    def post(self, request, id):
        serializer = SupportConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            recommendation = get_object_or_404(
                Recommendation.objects.select_for_update(), id=id
            )
            if Support.objects.filter(
                supporter=request.user, recommendation=recommendation
            ).exists():
                return Response(
                    {"detail": _("You already support this recommendation.")},
                    status=409,
                )
            supporter_number = (
                recommendation.supports.aggregate(Max("supporter_number"))[
                    "supporter_number__max"
                ]
                or 0
            ) + 1
            support = Support(
                supporter=request.user,
                recommendation=recommendation,
                supporter_number=supporter_number,
                amount_lamports=SUPPORT_AMOUNT_LAMPORTS,
                recommendation_cycle_number=recommendation.recommendation_cycle_number,
                on_chain_support_transaction=serializer.validated_data[
                    "transaction_signature"
                ],
                on_chain_support_account=serializer.validated_data.get(
                    "on_chain_support_account"
                ),
            )
            try:
                support.full_clean()
                support.save()
            except ValidationError:
                # Clean() rejects missing on-chain fields; a 400 tells the
                # client to fix its payload rather than surfacing a 500.
                return Response(
                    {"detail": _("Support could not be recorded.")},
                    status=400,
                )
            except IntegrityError:
                # Constraint safety net (duplicate signature / concurrent same
                # supporter): the client can retry with a fresh signature.
                return Response(
                    {
                        "detail": _(
                            "Support was not recorded; the transaction signature "
                            "may already be in use."
                        )
                    },
                    status=409,
                )
            now = timezone.now()
            recommendation.support_count += 1
            recommendation.last_support_at = now
            update_fields = ["support_count", "last_support_at", "updated_at"]
            if (
                recommendation.status == Recommendation.Status.INACTIVE
                and recommendation.recommender_participants.filter(
                    is_active=True
                ).exists()
            ):
                # Support-during-INACTIVE transition: an active recommender
                # stake means the recommendation is live again.
                recommendation.status = Recommendation.Status.ACTIVE
                recommendation.activated_at = now
                recommendation.deactivated_at = None
                update_fields += ["status", "activated_at", "deactivated_at"]
            # auto_now fields only persist when listed in update_fields.
            recommendation.save(update_fields=update_fields)
        return Response(
            SupportEnvelopeSerializer(
                instance={
                    "support": support,
                    "solana_hints": support_hints(
                        recommendation, support.supporter_number
                    ),
                }
            ).data,
            status=201,
        )


@extend_schema_view(
    post=extend_schema(
        summary="Confirm a support transaction",
        description=(
            "Authenticated only. Records the on-chain support after the client "
            "submits the signed transaction; idempotent when an Idempotency-Key "
            "header is supplied."
        ),
        request=SupportConfirmSerializer,
        responses={
            201: SupportEnvelopeSerializer,
            400: OpenApiResponse(description="Invalid signature or input."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
            409: OpenApiResponse(
                description="Already supported or idempotency key in use."
            ),
        },
    ),
)
class SupportConfirmView(IdempotencyKeyMixin, SupportConfirmBaseView):
    """POST /api/recommendations/{id}/support/confirm/ — confirm support."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationSupportThrottle]


class SupportListView(APIView):
    """GET /api/recommendations/{id}/supports/ — list supporters (public)."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List supporters",
        description=(
            "Public endpoint. Returns paginated supports ordered by supporter number."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of supports."),
            404: OpenApiResponse(description="Recommendation not found."),
        },
    )
    def get(self, request, id):
        recommendation = get_object_or_404(Recommendation, id=id)
        queryset = recommendation.supports.all().order_by("supporter_number")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            SupportReadSerializer(page, many=True).data
        )
