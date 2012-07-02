from __future__ import unicode_literals, division

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from yoi.account.user import bp as account
from yoi.config import secret, testing, database_url, use_debugger
from yoi.flask_genshi import Genshi

app = Flask(__name__)
genshi = Genshi(app)
app.db = SQLAlchemy(app)

app.register_blueprint(account)

# FIXME - Use app.config.from_object
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
#app.config['TESTING'] = testing
#app.config['CSRF_ENABLED'] = not testing
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SECRET_KEY'] = secret
