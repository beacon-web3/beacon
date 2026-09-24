"""Duplicate report views: file a report and admin listing."""

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.idempotency import IdempotencyKeyMixin
from recommendations.models import BookRecommendation, DuplicateReport
from recommendations.pagination import RecommendationPagination
from recommendations.serializers import (
    DuplicateReportCreateSerializer,
    DuplicateReportReadSerializer,
)
from recommendations.throttles import (
    RecommendationDuplicateThrottle,
    RecommendationReadThrottle,
)


class DuplicateReportBaseView(APIView):
    """POST file a PENDING duplicate report against a recommendation."""

    def post(self, request, id):
        recommendation = get_object_or_404(BookRecommendation, id=id)
        serializer = DuplicateReportCreateSerializer(
            data=request.data, context={"recommendation": recommendation}
        )
        serializer.is_valid(raise_exception=True)
        if DuplicateReport.objects.filter(
            reporter=request.user, recommendation=recommendation
        ).exists():
            return Response(
                {
                    "detail": _(
                        "You have already filed a report for this recommendation."
                    )
                },
                status=409,
            )
        suspected = serializer.validated_data.get("suspected_duplicate_of")
        # Only a non-null suspect can collide with the pair unique constraint
        # (PostgreSQL treats NULLs as distinct), so the pair pre-check is
        # skipped when no suspect was given.
        if (
            suspected is not None
            and DuplicateReport.objects.filter(
                reporter=request.user, suspected_duplicate_of=suspected
            ).exists()
        ):
            return Response(
                {
                    "detail": _(
                        "You have already filed a report against that "
                        "suspected duplicate."
                    )
                },
                status=409,
            )
        try:
            report = DuplicateReport.objects.create(
                reporter=request.user,
                recommendation=recommendation,
                suspected_duplicate_of=suspected,
                reason=serializer.validated_data.get("reason", ""),
            )
        except IntegrityError:
            # The exists() pre-checks are the common case; the DB unique
            # constraints are the safety net for concurrent requests (without
            # a shared Idempotency-Key). Only map conflicts on the two
            # reporter uniqueness constraints to 409; any other constraint
            # failure is a real DB fault and must surface as a 500.
            already_reported = DuplicateReport.objects.filter(
                reporter=request.user, recommendation=recommendation
            ).exists()
            pair_conflict = (
                suspected is not None
                and DuplicateReport.objects.filter(
                    reporter=request.user, suspected_duplicate_of=suspected
                ).exists()
            )
            if already_reported:
                return Response(
                    {
                        "detail": _(
                            "You have already filed a report for this recommendation."
                        )
                    },
                    status=409,
                )
            if pair_conflict:
                return Response(
                    {
                        "detail": _(
                            "You have already filed a report against that "
                            "suspected duplicate."
                        )
                    },
                    status=409,
                )
            raise
        return Response(
            {"duplicate_report": DuplicateReportReadSerializer(report).data},
            status=201,
        )


@extend_schema_view(
    post=extend_schema(
        summary="File a duplicate report",
        description=(
            "Authenticated only. Files a PENDING duplicate report against the "
            "recommendation; both suspected_duplicate_of and reason are "
            "optional, and self-reference is rejected with 400. Returns 409 "
            "when the caller already filed a report. Idempotent when an "
            "Idempotency-Key header is supplied."
        ),
        request=DuplicateReportCreateSerializer,
        responses={
            201: OpenApiResponse(description="Created duplicate report."),
            400: OpenApiResponse(
                description="Self-reference or unknown suspected duplicate."
            ),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
            409: OpenApiResponse(description="Report already filed."),
        },
    ),
)
class DuplicateReportView(IdempotencyKeyMixin, DuplicateReportBaseView):
    """POST /api/recommendations/{id}/report-duplicate/ — file a report.

    The explicit ``@extend_schema_view(post=...)`` is required: the
    ``IdempotencyKeyMixin`` sits first in the MRO and shadows
    ``DuplicateReportBaseView.post`` from drf-spectacular.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationDuplicateThrottle]


class DuplicateReportListView(APIView):
    """GET /api/recommendations/{id}/duplicate-reports/ — admin only."""

    permission_classes = [IsAdminUser]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List duplicate reports",
        description=(
            "Admin only. Returns paginated duplicate reports filed against "
            "the recommendation, newest first. Status transitions are "
            "handled through Django admin for MVP (Open Question 1)."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of reports."),
            403: OpenApiResponse(description="Admin only."),
            404: OpenApiResponse(description="Recommendation not found."),
        },
    )
    def get(self, request, id):
        recommendation = get_object_or_404(BookRecommendation, id=id)
        queryset = recommendation.duplicate_reports.select_related(
            "reporter",
            "recommendation__category",
            "suspected_duplicate_of__category",
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            DuplicateReportReadSerializer(page, many=True).data
        )
