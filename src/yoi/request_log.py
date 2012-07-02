from flask import request
import logging

from yoi.app import app

@app.before_request
def add_request_log():
    request.log = logging.getLogger('yoi')
