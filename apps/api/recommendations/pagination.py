from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class RecommendationPagination(PageNumberPagination):
    """Page-number pagination with the plan's results/count/page/page_size envelope.

    Default page size is 20, maximum 100 (Plan 0018 API Design Principles).
    """

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = MAX_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response(
            {
                "results": data,
                "count": self.page.paginator.count,
                "page": self.page.number,
                "page_size": self.get_page_size(self.request) or self.page_size,
            }
        )
