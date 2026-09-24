from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
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
from recommendations.models import CuratorFollow
from recommendations.pagination import RecommendationPagination
from recommendations.serializers import (
    CuratorFollowReadSerializer,
    CuratorFollowSerializer,
    ProfileSerializer,
    ReputationEventSerializer,
)
from recommendations.throttles import (
    RecommendationFollowThrottle,
    RecommendationReadThrottle,
)

Account = get_user_model()


class CuratorFollowToggleView(APIView):
    """POST follow / DELETE unfollow — authenticated only."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationFollowThrottle]

    @extend_schema(
        summary="Follow a curator",
        description="Authenticated only. Follows the given account.",
        request=CuratorFollowSerializer,
        responses={
            201: CuratorFollowReadSerializer,
            400: OpenApiResponse(description="Cannot follow yourself."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Account not found."),
            409: OpenApiResponse(description="Already following this account."),
        },
    )
    def post(self, request, username):
        target = get_object_or_404(Account, username=username)
        if target == request.user:
            return Response({"detail": _("You cannot follow yourself.")}, status=400)
        follow, created = CuratorFollow.objects.get_or_create(
            follower=request.user, followee=target
        )
        if not created:
            return Response(
                {"detail": _("You already follow this account.")}, status=409
            )
        return Response(CuratorFollowReadSerializer(follow).data, status=201)

    @extend_schema(
        summary="Unfollow a curator",
        description="Authenticated only. Removes the follow relationship.",
        responses={
            204: OpenApiResponse(description="Unfollowed."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Account or follow not found."),
        },
    )
    def delete(self, request, username):
        target = get_object_or_404(Account, username=username)
        follow = get_object_or_404(
            CuratorFollow, follower=request.user, followee=target
        )
        follow.delete()
        return Response(status=204)


@extend_schema_view(
    post=extend_schema(
        summary="Follow a curator",
        description=(
            "Authenticated only. Follows the given account; idempotent when an "
            "Idempotency-Key header is supplied."
        ),
        request=CuratorFollowSerializer,
        responses={
            201: CuratorFollowReadSerializer,
            400: OpenApiResponse(description="Cannot follow yourself."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Account not found."),
            409: OpenApiResponse(
                description="Already following this account, or idempotency key in use."
            ),
        },
    ),
)
class CuratorFollowView(IdempotencyKeyMixin, CuratorFollowToggleView):
    """POST /api/accounts/{username}/follow/ — idempotent follow toggle."""


class FollowersView(APIView):
    """GET followers (public) — paginated."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List followers",
        description=(
            "Public endpoint. Returns paginated followers of the given account."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of followers."),
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        target = get_object_or_404(Account, username=username)
        queryset = (
            target.followers.all()
            .select_related("follower", "followee")
            .order_by("-created_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            CuratorFollowReadSerializer(page, many=True).data
        )


class FollowingView(APIView):
    """GET following (public) — paginated."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List following",
        description=(
            "Public endpoint. Returns paginated accounts the given account follows."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of following."),
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        target = get_object_or_404(Account, username=username)
        queryset = (
            target.following.all()
            .select_related("follower", "followee")
            .order_by("-created_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            CuratorFollowReadSerializer(page, many=True).data
        )


class ReputationView(APIView):
    """GET reputation events (public) — paginated."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List reputation events",
        description=(
            "Public endpoint. Returns paginated reputation event history "
            "for the account."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of reputation events."),
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        target = get_object_or_404(Account, username=username)
        queryset = (
            target.reputation_events.all()
            .prefetch_related("recommendation__categories")
            .order_by("-created_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            ReputationEventSerializer(page, many=True).data
        )


class ProfileView(APIView):
    """GET public profile (public)."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]

    @extend_schema(
        summary="Get public profile",
        description=(
            "Public endpoint. Returns display name, reputation score, and badge count."
        ),
        responses={
            200: ProfileSerializer,
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        target = get_object_or_404(Account, username=username)
        return Response(ProfileSerializer(target).data)
