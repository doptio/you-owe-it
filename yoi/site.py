from __future__ import unicode_literals, division

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

from dweeb.config import secret, testing, db_url
from dweeb.flask_genshi import Genshi
from dweeb.middleware import wrap_application
from yoi.pages import add_url_rules

import dweeb.account.user

resources = {}

app = Flask(__name__)
# FIXME - Use app.config.from_object
app.config['TESTING'] = testing
app.config['CSRF_ENABLED'] = not testing
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SECRET_KEY'] = secret
app.wsgi_app = wrap_application(app.wsgi_app)

genshi = Genshi(app)
app.db = SQLAlchemy(app)

add_url_rules(app)
app.register_blueprint(dweeb.account.user.bp)
