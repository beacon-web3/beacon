"""Bookmark views: toggle, idempotent toggle, and current-user listing."""

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.idempotency import IdempotencyKeyMixin
from recommendations.models import Bookmark, Recommendation
from recommendations.pagination import RecommendationPagination
from recommendations.serializers import BookmarkReadSerializer, BookmarkSerializer
from recommendations.throttles import (
    RecommendationBookmarkThrottle,
    RecommendationReadThrottle,
)


class BookmarkToggleView(APIView):
    """POST bookmark / DELETE remove — authenticated only."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationBookmarkThrottle]

    @extend_schema(
        summary="Bookmark a recommendation",
        description=(
            "Authenticated only. Bookmarks the recommendation for the current user."
        ),
        request=BookmarkSerializer,
        responses={
            201: BookmarkReadSerializer,
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
            409: OpenApiResponse(description="Recommendation already bookmarked."),
        },
    )
    def post(self, request, id):
        recommendation = get_object_or_404(Recommendation, id=id)
        bookmark, created = Bookmark.objects.get_or_create(
            account=request.user, recommendation=recommendation
        )
        if not created:
            return Response(
                {"detail": _("Recommendation already bookmarked.")}, status=409
            )
        return Response(
            BookmarkReadSerializer(bookmark).data,
            status=201,
        )

    @extend_schema(
        summary="Remove a bookmark",
        description="Authenticated only. Removes the current user's bookmark.",
        responses={
            204: OpenApiResponse(description="Bookmark removed."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation or bookmark not found."),
        },
    )
    def delete(self, request, id):
        recommendation = get_object_or_404(Recommendation, id=id)
        bookmark = get_object_or_404(
            Bookmark, account=request.user, recommendation=recommendation
        )
        bookmark.delete()
        return Response(status=204)


@extend_schema_view(
    post=extend_schema(
        summary="Bookmark a recommendation",
        description=(
            "Authenticated only. Bookmarks the recommendation for the current "
            "user; idempotent when an Idempotency-Key header is supplied."
        ),
        request=BookmarkSerializer,
        responses={
            201: BookmarkReadSerializer,
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Recommendation not found."),
            409: OpenApiResponse(
                description="Already bookmarked, or idempotency key in use."
            ),
        },
    ),
)
class BookmarkView(IdempotencyKeyMixin, BookmarkToggleView):
    """POST /api/recommendations/{id}/bookmark/ — idempotent bookmark toggle."""


class UserBookmarksView(APIView):
    """GET current user's bookmarks — authenticated only."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List my bookmarks",
        description=(
            "Authenticated only. Returns the current user's bookmarks, newest first."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of bookmarks."),
            403: OpenApiResponse(description="Not authenticated."),
        },
    )
    def get(self, request):
        queryset = (
            request.user.bookmarks.all()
            .prefetch_related("recommendation__categories")
            .order_by("-created_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            BookmarkReadSerializer(page, many=True).data
        )
