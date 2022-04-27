class Request:
    def __init__(self, environ: dict):
        self.method = environ['REQUEST_METHOD'].lower()
        self.GET = self._get_params(environ['QUERY_STRING'])
        self.POST = self._post_params(environ['wsgi.input'].read())
    
    def _get_params(self, qs: str) -> dict:
        return qs
    
    def _post_params(self, raw_bytes: bytes) -> dict:
        return raw_bytes.decode("utf-8")