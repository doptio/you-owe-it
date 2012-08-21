from __future__ import unicode_literals, division

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from raven import Client
from raven.middleware import Sentry

from yoi.account.user import bp as account
from yoi.config import secret, testing, database_url, use_debugger
from yoi.flask_genshi import Genshi, render_response
from yoi import middleware

app = Flask(__name__)
app.genshi = Genshi(app)
app.db = SQLAlchemy(app)

app.register_blueprint(account)

# FIXME - Use app.config.from_object
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
#app.config['TESTING'] = testing
#app.config['CSRF_ENABLED'] = not testing
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SECRET_KEY'] = secret

# Nice error pages
@app.errorhandler(404)
def not_found(e):
    return render_response('404.html'), 404

# Error-reporting middleware
if 'SENTRY_URL' in os.environ:
    app.wsgi_app = Sentry(app.wsgi_app, Client(os.environ['SENTRY_URL']))

# Nice 'Internal Server Error' page
error_page = (app.genshi
                .template_loader.load('500.html')
                .generate(g={'user': None},
                          get_flashed_messages=lambda **kwargs: [])
                .render('html'))
if os.environ.get('ENVIRONMENT') == 'production':
    app.wsgi_app = middleware.error_page(app.wsgi_app, error_page)
