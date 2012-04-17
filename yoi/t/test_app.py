from __future__ import unicode_literals, division

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from dweeb.testing import setup_module, assert_eq

from yoi.app import app

def test_index():
    client = Client(app, BaseResponse)
    resp = client.get('/')
    assert_eq(resp.status_code, 200)
