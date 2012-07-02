from flask import Blueprint, redirect, url_for, flash
from flask import current_app as app, request, g, session
from flask.ext.wtf import Form, TextField, Required
from sqlalchemy import Column, Integer, String

from openid.consumer.consumer import Consumer, SUCCESS
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import sreg

from dweeb.account.openid_store import MemcacheStore
from dweeb.flask_genshi import render

bp = Blueprint('account', __name__,
               template_folder='templates')

### FIXME - Only premit one registration!
@bp.before_app_request
def get_current_user():
    if session.get('user_id'):
        g.user = app.db.User.get(session['user_id'])
    else:
        g.user = None


@bp.record
def database_setup(state):
    db = state.app.db

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)

        @classmethod
        def get(cls, user_id):
            return app.db.session.query(cls).get(user_id)

    class OpenId(db.Model):
        openid = db.Column(db.String, primary_key=True)
        user_id = db.Column('user', db.Integer, db.ForeignKey('user.id'),
                            nullable=False)
        user = db.relationship(User)

    db.User = User
    db.OpenId = OpenId


class LoginForm(Form):
    openid = TextField('Your OpenID', validators=[Required()])

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        realm = url_for('index', _external=True)
        return_to = url_for('.openid_return', _external=True)

        try:
            auth_req = make_consumer().begin(form.openid.data)
            auth_req.addExtension(sreg.SRegRequest(optional=['nickname',
                                                             'fullname']))
            return redirect(auth_req.redirectURL(realm, return_to))

        except DiscoveryFailure, e:
            form.errors['openid'] = [e.message]

    return render('account/login.html', form=form)

def make_consumer():
    # FIXME - This will not work on Heroku.
    openid_store = MemcacheStore()
    consumer = Consumer(session, openid_store)
    return consumer

@bp.route('/openid-return')
def openid_return():
    return_to = url_for('.openid_return', _external=True)
    result = make_consumer().complete(request.args, return_to)

    if result.status <> SUCCESS:
        flash('OpenID authentication failed', 'error')
        return redirect(url_for('.login'))

    db = app.db
    user = (db.User.query.join(db.OpenId)
                # FIXME -- is identity_url the right thing?
                .filter(db.OpenId.openid == result.identity_url)
                .first())

    if user:
        session['user_id'] = user.id
        return redirect(url_for('home'))

    extra = sreg.SRegResponse.fromSuccessResponse(result)
    if extra:
        extra = extra.data
    else:
        extra = {}

    name = None
    for key in ['fullname', 'nickname']:
        if key in extra:
            name = extra[key]
            break

    ### FIXME - Assign to existing user if we have a session!
    user = db.User(name=name)
    db.session.add(user)
    openid = db.OpenId(user=user, openid=result.identity_url)
    db.session.add(openid)
    db.session.commit()

    session['user_id'] = user.id

    if name:
        flash('Welcome, %s!' % name)
    return redirect(url_for('.register'))

class RegisterForm(Form):
    name = TextField('name', validators=[Required()])

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if not 'user_id' in session:
        return redirect('/login')

    form = RegisterForm()
    if form.validate_on_submit():
        user = app.db.User.get(session['user_id'])
        user.name = form.name.data
        app.db.session.commit()

        flash('Pleased to meet you, %s!' % form.name.data)
        return redirect(url_for('home'))

    return render('account/register.html', form=form)


@bp.route('/logout')
def logout():
    del session['user_id']
    return redirect(url_for('index'))
