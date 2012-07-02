from __future__ import unicode_literals, division

from flask import request, g, redirect, url_for

from yoi.app import app
from yoi import authentication
from yoi import loggy
from yoi import pages
from yoi import schema

user_needful_paths = set(['/home', '/settings', '/new-event'])

@app.before_request
def redirect_account_pages():
    if request.path in user_needful_paths and not g.user:
        return redirect(url_for('account.login'))

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=0)
    app.run('0.0.0.0', port=4000)
