from __future__ import unicode_literals, division

from wsgi_lite import lite, lighten
from wsgiref.headers import Headers

from dweeb.config import use_debugger
from dweeb.loggy import loggy_context, loggy_context_manager

__all__ = ['wrap_application']


def wrap_application(app):
    'Wrap WSGI application with default and configure middlewares.'

    app = loggy(app)

    if use_debugger:
        from werkzeug.debug import DebuggedApplication
        app = DebuggedApplication(app, evalex=True)

    return app


def loggy(app):
    'WSGI middleware for adding request info to log output.'

    app = lighten(app)

    @lite
    def loggy_middleware(environ):
        with loggy_context_manager():
            loggy_context.request_id = environ.get('HTTP_X_VARNISH', '-')
            return app(environ)

    return loggy_middleware
