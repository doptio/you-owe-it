import logging
import os
from wsgi_lite import lite, lighten

__all__ = ['error_page']

here = os.path.dirname(__file__)
log = logging.getLogger(__name__)

def error_page(app, html):
    'WSGI middleware for serving static "Internal Server Error" page.'

    app = lighten(app)

    error_response = ('500 Internal Server Error',
                      [('Content-Type', 'text/html; charset=utf-8')],
                      [html])

    @lite
    def error_page_middleware(environ):
        try:
            return app(environ)
        except Exception:
            log.error('Uncaught exception', exc_info=True)
            return error_response

    return error_page_middleware
