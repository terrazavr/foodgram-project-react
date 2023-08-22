from rest_framework.pagination import PageNumberPagination

from foodgram.constants import PAGE_SIZE


class LimitNumberPagination(PageNumberPagination):
    page_size_query_param = "limit"
    page_size = PAGE_SIZE
