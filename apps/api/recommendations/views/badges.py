"""Badge listing views: badges for a recommendation and for an account."""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from recommendations.models import Recommendation
from recommendations.pagination import RecommendationPagination
from recommendations.serializers import BadgeSerializer
from recommendations.throttles import RecommendationReadThrottle

Account = get_user_model()


class RecommendationBadgeListView(APIView):
    """GET badges for a recommendation (public) — paginated."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List recommendation badges",
        description="Public endpoint. Returns badges earned for the recommendation.",
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of badges."),
            404: OpenApiResponse(description="Recommendation not found."),
        },
    )
    def get(self, request, id):
        recommendation = get_object_or_404(Recommendation, id=id)
        queryset = (
            recommendation.badges.all()
            .select_related("account")
            .prefetch_related("recommendation__categories")
            .order_by("-earned_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(BadgeSerializer(page, many=True).data)


class AccountBadgeListView(APIView):
    """GET badges earned by an account (public) — paginated."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List account badges",
        description="Public endpoint. Returns badges earned by the account.",
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of badges."),
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        account = get_object_or_404(Account, username=username)
        queryset = (
            account.badges.all()
            .select_related("account")
            .prefetch_related("recommendation__categories")
            .order_by("-earned_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(BadgeSerializer(page, many=True).data)
