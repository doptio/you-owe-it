from __future__ import unicode_literals, division

from flask import request, g, redirect, url_for

from yoi.app import app
from yoi import authentication
from yoi import request_log
from yoi import pages
from yoi import schema

user_needful_paths = set(['/home', '/settings', '/new-event'])
admin_users = set(['s@doptio.com', 'f@doptio.com'])

@app.before_request
def redirect_account_pages():
    if request.path in user_needful_paths and not g.user:
        return redirect(url_for('account.login'))

@app.before_request
def protect_admin_pages():
    if not request.path.startswith('/admin/'):
        return
    if g.user and g.user.email in admin_users:
        return
    return redirect(url_for('account.login', r=request.path))

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=0)
    app.run('0.0.0.0', port=4000)
