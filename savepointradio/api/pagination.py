from rest_framework import pagination
from rest_framework.response import Response


class TotalPagesPagination(pagination.PageNumberPagination):
    '''
    Custom pagination class to add the total numer of pages for the results.

    (Thanks to https://stackoverflow.com/questions/40985248/)
    '''
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
