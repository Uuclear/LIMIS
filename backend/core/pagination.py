from __future__ import annotations

from collections import OrderedDict
from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data: list[Any]) -> Response:
        return Response(OrderedDict([
            ('code', 200),
            ('message', 'success'),
            ('data', OrderedDict([
                ('count', self.page.paginator.count),
                ('page', self.page.number),
                ('page_size', self.get_page_size(self.request)),
                ('results', data),
            ])),
        ]))

    def get_paginated_response_schema(self, schema: dict) -> dict:
        return {
            'type': 'object',
            'properties': {
                'code': {'type': 'integer', 'example': 200},
                'message': {'type': 'string', 'example': 'success'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer'},
                        'page': {'type': 'integer'},
                        'page_size': {'type': 'integer'},
                        'results': schema,
                    },
                },
            },
        }
