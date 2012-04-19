from flask import request
from flask import current_app as app
from flaskext.genshi import render_response

def page():
    return render_response('index.html')

def add_url_rules(app):
    app.add_url_rule('/', 'index', page)
