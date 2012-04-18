from __future__ import unicode_literals, division

from flask import Flask
from flaskext.genshi import Genshi

from dweeb.middleware import wrap_application
from dweeb.resources import dweeb_resources

from yoi.pages import add_url_rules

resources = {}
resources.update(dweeb_resources)

app = Flask(__name__)
genshi = Genshi(app)
app.wsgi_app = wrap_application(app.wsgi_app)

add_url_rules(app)
