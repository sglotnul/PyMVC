class View:
    def post(self, request):
        pass

    def get(self, request):
        pass

    def __call__(self, request) -> object:
        func = getattr(self, request.method)
        return func(request)