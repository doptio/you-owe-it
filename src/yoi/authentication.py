from flask import g, session

from yoi.app import app

@app.before_request
def get_current_user():
    if session.get('user_id'):
        g.user = app.db.User.get(session['user_id'])
    else:
        g.user = None
