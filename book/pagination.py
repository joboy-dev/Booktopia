from rest_framework.pagination import PageNumberPagination

class BooksPagination(PageNumberPagination):
    '''Pagination class for books'''

    page_size = 5
    page_query_param = 'page'
    max_page_size = 10
    page_size_query_param = 'size'
