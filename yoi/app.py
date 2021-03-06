from __future__ import unicode_literals, division

from flask import Flask, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
import os
from raven import Client
from raven.middleware import Sentry

from yoi.account.user import bp as account
from yoi.config import (secret,
                        database_url,
                        in_production,
                        canonical_domain,
                        always_secure)
from yoi import dweeb
from yoi.flask_genshi import Genshi, render_response
from yoi import middleware
from yoi.resources import static_url

app = Flask(__name__)
app.request_class = dweeb.Request

app.genshi = Genshi(app)
app.db = SQLAlchemy(app)

app.register_blueprint(account)

# FIXME - Use app.config.from_object
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SECRET_KEY'] = secret

if canonical_domain:
    app.config['SESSION_COOKIE_DOMAIN'] = canonical_domain
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = always_secure

# Global HTTP response headers
cache_headers = [
    ('Cache-Control', 'public'),
]
no_cache_headers = [
    ('Cache-Control', 'no-cache'),
    ('Expires', 'Sat, 07 Jul 1979 23:00:00 GMT'),
]
hsts_headers = [
    ('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'),
]


@app.after_request
def add_global_headers(response):
    expires = getattr(response, 'expires', None)
    if expires:
        response.headers.extend(cache_headers)
    else:
        response.headers.extend(no_cache_headers)

    if request.is_secure:
        response.headers.extend(hsts_headers)

    return response


@app.before_request
def canonical_redirect():
    if always_secure and not request.is_secure:
        return redirect(request.url.replace('http://', 'https://'))
    if canonical_domain and request.host != canonical_domain:
        return redirect(request.url.replace('://' + request.host,
                                            '://' + canonical_domain))


# Nice error pages
@app.errorhandler(404)
def not_found(e):
    return render_response('404.html'), 404

# Error-reporting middleware
if 'SENTRY_URL' in os.environ:
    app.wsgi_app = Sentry(app.wsgi_app, Client(os.environ['SENTRY_URL']))


# Nice 'Internal Server Error' page
# FIXME - should use render_template.
with app.test_request_context('/'):
    error_page = (app.genshi
                  .template_loader.load('500.html')
                  .generate(g={'user': None},
                            get_flashed_messages=lambda **kwargs: [],
                            static_url=static_url)
                  .render('html'))

if in_production:
    app.wsgi_app = middleware.error_page(app.wsgi_app, error_page)
