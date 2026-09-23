from django.db import IntegrityError, transaction
from django.db.models import Max, Q
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
from recommendations.models import (
    SUPPORT_AMOUNT_LAMPORTS,
    BookRecommendation,
    RecommenderParticipant,
    Support,
)
from recommendations.pagination import RecommendationPagination
from recommendations.serializers import (
    CreateRecommendationSerializer,
    ReactivateSerializer,
    RecommendationDetailSerializer,
    RecommendationEnvelopeSerializer,
    RecommendationListEnvelopeSerializer,
    RecommendationSummarySerializer,
    RecommenderParticipantSerializer,
    RecommendSerializer,
    SupportConfirmSerializer,
    SupportCreateSerializer,
    SupportEnvelopeSerializer,
    SupportPrepareEnvelopeSerializer,
    SupportReadSerializer,
    UpdateRecommendationSerializer,
)
from recommendations.throttles import (
    RecommendationActThrottle,
    RecommendationBookmarkThrottle,
    RecommendationCreateThrottle,
    RecommendationDuplicateThrottle,
    RecommendationReadThrottle,
    RecommendationStakeThrottle,
    RecommendationSupportThrottle,
)

# Placeholder views for later Plan 0018 phases. Permission and throttle classes
# reflect the plan's rate/permission matrix so public reads stay public.

SEARCH_MIN_LENGTH = 3
ORDERING_CHOICES = {"-support_count", "created_at", "-created_at"}
LIST_FILTER_PARAMETERS = [
    OpenApiParameter(
        name="status",
        type=str,
        description="Lifecycle status filter: ACTIVE|INACTIVE.",
    ),
    OpenApiParameter(
        name="page_type",
        type=str,
        description="Page type filter: STANDALONE_WORK|RECOGNIZED_SERIES.",
    ),
    OpenApiParameter(
        name="category",
        type=str,
        description="Category slug filter.",
    ),
    OpenApiParameter(
        name="duplicate_risk_status",
        type=str,
        description="Duplicate risk filter: LOW_RISK|HIGH_RISK|NEEDS_REVIEW.",
    ),
    OpenApiParameter(
        name="review_status",
        type=str,
        description="Review status filter: NOT_REQUIRED|PENDING|APPROVED|REJECTED.",
    ),
    OpenApiParameter(
        name="creator",
        type=str,
        description="Creator username filter.",
    ),
    OpenApiParameter(
        name="is_canonical",
        type=bool,
        description="Filter by canonical status (true|false).",
    ),
    OpenApiParameter(
        name="search",
        type=str,
        description="Search title or author names. Minimum 3 characters; "
        "shorter queries return an empty result set.",
    ),
    OpenApiParameter(
        name="ordering",
        type=str,
        description="Sort order: -support_count, created_at, -created_at.",
    ),
    OpenApiParameter(name="page", type=int, description="Page number."),
    OpenApiParameter(name="page_size", type=int, description="Page size (max 100)."),
]

# The support amount (SUPPORT_AMOUNT_LAMPORTS) lives in recommendations.models;
# the program ID is a placeholder until the Solana program is deployed.
SOLANA_PROGRAM_ID = "BeaconRecommendationProgramPlaceholder01"


def activation_hints(recommendation, amount_lamports, account):
    """Return Solana hints for an activation (recommend/reactivate).

    PDA seeds/addresses are placeholders: the client sends the stake
    transaction to the Beacon program, which derives the real PDAs. The
    wallet seed uses the account wallet address when present.
    """
    wallet = account.wallet_address or account.username
    return {
        "program_id": SOLANA_PROGRAM_ID,
        "stake_account_pda": f"stake_{recommendation.id}_{wallet}",
        "recommendation_account": f"rec_{recommendation.id}",
        "amount_lamports": amount_lamports,
        "pda_seeds": ["stake", str(recommendation.id), wallet],
    }


def support_hints(recommendation, supporter_number):
    """Return Solana hints for a support transaction (quote + confirm)."""
    return {
        "program_id": SOLANA_PROGRAM_ID,
        "support_account_pda": f"support_{recommendation.id}_{supporter_number}",
        "recommendation_account": f"rec_{recommendation.id}",
        "amount_lamports": SUPPORT_AMOUNT_LAMPORTS,
        "pda_seeds": ["support", str(recommendation.id), str(supporter_number)],
    }


class RecommendationCreateView(APIView):
    """POST /api/recommendations/ — create a recommendation (INACTIVE)."""

    @extend_schema(
        summary="Create a recommendation",
        description=(
            "Protected endpoint. Creates a recommendation with status INACTIVE. "
            "Idempotent via the Idempotency-Key header."
        ),
        request=CreateRecommendationSerializer,
        responses={
            201: RecommendationEnvelopeSerializer,
            400: OpenApiResponse(description="Invalid input or canonical duplicate."),
            403: OpenApiResponse(description="Not authenticated."),
        },
    )
    def post(self, request):
        serializer = CreateRecommendationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            recommendation = BookRecommendation.objects.create(
                creator=request.user, **serializer.validated_data
            )
        except IntegrityError:
            # DB unique constraint is the safety net for the serializer check;
            # a concurrent create of the same canonical work loses cleanly.
            return Response(
                {
                    "title": [
                        _(
                            "A canonical recommendation for this title and "
                            "author already exists."
                        )
                    ]
                },
                status=400,
            )
        return Response(
            {"recommendation": RecommendationDetailSerializer(recommendation).data},
            status=201,
        )


@extend_schema_view(
    post=extend_schema(
        summary="Create a recommendation",
        description=(
            "Authenticated only. Creates an INACTIVE recommendation; idempotent "
            "when an Idempotency-Key header is supplied."
        ),
        request=CreateRecommendationSerializer,
        responses={
            201: RecommendationEnvelopeSerializer,
            400: OpenApiResponse(description="Invalid input or canonical duplicate."),
            403: OpenApiResponse(description="Not authenticated."),
        },
    ),
)
class RecommendationListView(IdempotencyKeyMixin, RecommendationCreateView):
    """GET list (public, filtered, paginated) / POST create (idempotent).

    The explicit ``@extend_schema_view(post=...)`` above is required, not
    decorative: ``IdempotencyKeyMixin`` sits first in the MRO and shadows
    ``RecommendationCreateView.post``, so drf-spectacular cannot see the
    inherited ``@extend_schema`` on the base class.

    POST throttles with the create scope (10/min); GET uses the read scope
    (60/min) via ``get_throttles()``.
    """

    permission_classes = [AllowAny]
    pagination_class = RecommendationPagination

    def get_throttles(self):
        if self.request.method == "POST":
            return [RecommendationCreateThrottle()]
        return [RecommendationReadThrottle()]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def _filter_queryset(self, queryset, params):
        if status_filter := params.get("status"):
            queryset = queryset.filter(status=status_filter)
        if page_type := params.get("page_type"):
            queryset = queryset.filter(page_type=page_type)
        if category_slug := params.get("category"):
            queryset = queryset.filter(category__slug=category_slug)
        if risk := params.get("duplicate_risk_status"):
            queryset = queryset.filter(duplicate_risk_status=risk)
        if review := params.get("review_status"):
            queryset = queryset.filter(review_status=review)
        if creator_username := params.get("creator"):
            queryset = queryset.filter(creator__username=creator_username)
        if is_canonical := params.get("is_canonical"):
            if is_canonical in ("true", "false"):
                queryset = queryset.filter(is_canonical=is_canonical == "true")
        search = params.get("search")
        if search is not None:
            if len(search) >= SEARCH_MIN_LENGTH:
                queryset = queryset.filter(
                    Q(title__icontains=search) | Q(author_names__icontains=search)
                )
            else:
                # Short queries (including an empty `?search=`) return an empty
                # set rather than scanning the full table (plan: search
                # requires >= 3 characters).
                return queryset.none()
        if ordering := params.get("ordering"):
            if ordering in ORDERING_CHOICES:
                queryset = queryset.order_by(ordering)
        return queryset

    @extend_schema(
        summary="List recommendations",
        description=(
            "Public endpoint. Returns paginated canonical recommendation "
            "summaries with filtering. Search requires at least 3 characters."
        ),
        parameters=LIST_FILTER_PARAMETERS,
        responses={
            200: RecommendationListEnvelopeSerializer,
        },
    )
    def get(self, request):
        queryset = BookRecommendation.objects.select_related(
            "category", "creator", "current_recommender"
        )
        queryset = self._filter_queryset(queryset, request.query_params)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            return paginator.get_paginated_response(
                RecommendationSummarySerializer(page, many=True).data
            )
        return Response(RecommendationSummarySerializer(queryset, many=True).data)


class RecommendationUpdateView(APIView):
    """PATCH /api/recommendations/{id}/ — update creator-owned metadata.

    Only allowed before the first activation (cycle number 0, status INACTIVE).
    """

    @extend_schema(
        summary="Update a recommendation",
        description=(
            "Creator-only. Updates metadata fields before first activation "
            "(status INACTIVE and recommendation_cycle_number 0)."
        ),
        request=UpdateRecommendationSerializer,
        responses={
            200: RecommendationEnvelopeSerializer,
            400: OpenApiResponse(description="Already activated or invalid input."),
            403: OpenApiResponse(description="Not the creator."),
            404: OpenApiResponse(description="Recommendation not found."),
        },
    )
    def patch(self, request, id):
        recommendation = get_object_or_404(
            BookRecommendation.objects.select_related(
                "category", "creator", "current_recommender"
            ),
            id=id,
        )
        if request.user.is_anonymous or request.user != recommendation.creator:
            return Response(
                {
                    "detail": _(
                        "You do not have permission to update this recommendation."
                    )
                },
                status=403,
            )
        if (
            recommendation.recommendation_cycle_number > 0
            or recommendation.status != BookRecommendation.Status.INACTIVE
        ):
            return Response(
                {
                    "detail": _(
                        "Only inactive recommendations before their first "
                        "activation can be updated."
                    )
                },
                status=400,
            )
        serializer = UpdateRecommendationSerializer(
            instance=recommendation, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data:
            for field, value in serializer.validated_data.items():
                setattr(recommendation, field, value)
            # auto_now fields only persist when listed in update_fields.
            update_fields = [*serializer.validated_data.keys(), "updated_at"]
            recommendation.save(update_fields=update_fields)
        return Response(
            {"recommendation": RecommendationDetailSerializer(recommendation).data}
        )


class RecommendationDetailView(RecommendationUpdateView):
    """GET detail (full for authenticated, summary for anonymous) / PATCH update."""

    permission_classes = [AllowAny]
    # PATCH inherits the read throttle; the plan defines no dedicated update
    # scope, so read (60/min) is the only rate applied here.
    throttle_classes = [RecommendationReadThrottle]

    @extend_schema(
        summary="Retrieve a recommendation",
        description=(
            "Public endpoint. Authenticated requests receive the full detail "
            "serializer; anonymous requests receive the summary serializer."
        ),
        responses={
            200: RecommendationEnvelopeSerializer,
            404: OpenApiResponse(description="Recommendation not found."),
        },
    )
    def get(self, request, id):
        recommendation = get_object_or_404(
            BookRecommendation.objects.select_related(
                "category", "creator", "current_recommender"
            ),
            id=id,
        )
        if request.user.is_authenticated:
            data = RecommendationDetailSerializer(recommendation).data
        else:
            data = RecommendationSummarySerializer(recommendation).data
        return Response({"recommendation": data})


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
                BookRecommendation.objects.select_for_update(), id=id
            )
            if recommendation.status == BookRecommendation.Status.ACTIVE:
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
            recommendation.status = BookRecommendation.Status.ACTIVE
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
        recommendation = get_object_or_404(BookRecommendation, id=id)
        if Support.objects.filter(
            supporter=request.user, recommendation=recommendation
        ).exists():
            return Response(
                {"detail": _("You already support this recommendation.")}, status=409
            )
        supporter_number = recommendation.supports.count() + 1
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
                BookRecommendation.objects.select_for_update(), id=id
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
            support.full_clean()
            support.save()
            now = timezone.now()
            recommendation.support_count += 1
            recommendation.last_support_at = now
            update_fields = ["support_count", "last_support_at", "updated_at"]
            if (
                recommendation.status == BookRecommendation.Status.INACTIVE
                and recommendation.recommender_participants.filter(
                    is_active=True
                ).exists()
            ):
                # Support-during-INACTIVE transition: an active recommender
                # stake means the recommendation is live again.
                recommendation.status = BookRecommendation.Status.ACTIVE
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
        recommendation = get_object_or_404(BookRecommendation, id=id)
        queryset = recommendation.supports.all().order_by("supporter_number")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            return paginator.get_paginated_response(
                SupportReadSerializer(page, many=True).data
            )
        return Response(SupportReadSerializer(queryset, many=True).data)


class StakeView(APIView):
    """Placeholder — POST add stake / DELETE reclaim, implemented in Phase 5."""

    throttle_classes = [RecommendationStakeThrottle]


class StakeHistoryView(APIView):
    """Placeholder — GET stake history, implemented in Phase 5."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class BookmarkView(APIView):
    """Placeholder — POST create bookmark / DELETE remove, implemented in Phase 4."""

    throttle_classes = [RecommendationBookmarkThrottle]


class UserBookmarksView(APIView):
    """Placeholder — GET current user's bookmarks, implemented in Phase 4."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class RecommendationBadgeListView(APIView):
    """Placeholder — GET badges for a recommendation, implemented in Phase 4."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class AccountBadgeListView(APIView):
    """Placeholder — GET badges for an account, implemented in Phase 4."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class DuplicateReportView(APIView):
    """Placeholder — POST create duplicate report, implemented in Phase 5."""

    throttle_classes = [RecommendationDuplicateThrottle]


class DuplicateReportListView(APIView):
    """Placeholder — GET duplicate reports (admin-only), implemented in Phase 5."""
