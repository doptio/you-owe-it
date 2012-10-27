'Double-plus-good extra features for Flask.'

from __future__ import unicode_literals, division

import flask
from werkzeug._internal import _empty_stream
from werkzeug.utils import cached_property

class Request(flask.Request):
    max_content_length = 64 * 1024

    ### FIXME - Need to set remote_addr from CF-Connecting-IP /
    ### X-Forwarded-For!

    @cached_property
    def is_secure(self):
        '`True` if the request is secure.'
        # Work-around for Heroku not following nginx's lead.
        if 'HTTP_X_FORWARDED_PROTO' in self.environ:
            return self.environ.get('HTTP_X_FORWARDED_PROTO') == 'https'
        return self.environ['wsgi.url_scheme'] == 'https'

    @cached_property
    def data(self):
        'The string representation of the request body.'
        # Damn it, Werkzeug. If I ask for the raw bytes POST'ed, I want them
        # no matter what the fucking content-type may say.

        # This is the marker that BaseRequest uses to determine if it has
        # parsed a request.
        assert 'stream' not in self.__dict__
        self.stream = _empty_stream

        length = self.headers.get('content-length', type=int)
        return self.input_stream.read(length)
