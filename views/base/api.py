import tornado.web

from paginators.page_number import PageNumberPagination


class APIView(tornado.web.RequestHandler):
    serializer_class = None
    filter_class = None
    pagination_class = PageNumberPagination
    _paginator = None
    args = []
    kwargs = {}

    def get_queryset(self):
        raise NotImplementedError

    def get_filter(self, *args, **kwargs):
        filter_class = self.get_filter_class()
        if not filter_class:
            return
        kwargs['context'] = self.filter_context()
        return filter_class(*args, **kwargs)

    def get_filter_class(self):
        return self.filter_class

    def filter_context(self):
        return {
            'request': self.request,
            'handler': self
        }

    def filter_queryset(self, queryset):
        filter_instance = self.get_filter()
        if filter_instance:
            queryset = filter_instance.filter_queryset(queryset)
        return queryset

    @property
    def paginator(self):
        if not self._paginator:
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {
            'request': self.request,
            'view': self
        }

    def write_response(self, response):
        for name, value in response.header_items():
            self.set_header(name, value)
        self.write(response.render())
