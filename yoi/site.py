from __future__ import unicode_literals, division

from flask import Flask

from dweeb.config import secret
from dweeb.flask_genshi import Genshi
from dweeb.middleware import wrap_application
from yoi.pages import add_url_rules

import dweeb.account.user

resources = {}

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SECRET_KEY'] = secret
app.wsgi_app = wrap_application(app.wsgi_app)

add_url_rules(app)
app.register_blueprint(dweeb.account.user.bp)

genshi = Genshi(app)
