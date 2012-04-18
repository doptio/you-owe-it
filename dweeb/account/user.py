from flask import Blueprint, request, g, session, redirect, url_for, flash
from flask.ext.wtf import Form, TextField, Required

from openid.consumer.consumer import Consumer, SUCCESS
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import sreg

from dweeb.account.openid_store import MemcacheStore
from dweeb.flask_genshi import render

bp = Blueprint('account.user', __name__,
               template_folder='templates')

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

    flash('Welcome, %s' % result.identity_url)
    extra = sreg.SRegResponse.fromSuccessResponse(result)
    if extra:
        for key, value in extra.data.items():
            flash('I see you! (%s: %s)' % (key, value))
    return redirect(url_for('index'))

    '''
    user = ctx.store.get_user_for_openid(result.identity_url)
    if user:
        login = ctx.request.session['user'] = user['login']
        ctx.response.location = ctx.adapter.build('user_tag',
                                                  {'user': login})
    else:
        ctx.request.session['openid'] = result.identity_url
        ctx.response.location = ctx.adapter.build('register')
    '''

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        ctx.values['openid'] = ctx.request.session.get('openid', 'imposter')
        return render_response('account/register.html')

    elif request.method == 'POST':
        openid = ctx.values['openid'] = ctx.request.session.get('openid')
        if not openid:
            ctx.response.status_code = 302
            ctx.response.location = ctx.adapter.build('login')
            return

        login = ctx.request.form.get('login')
        if ctx.store.register_user(login, openid):
            del ctx.request.session['openid']
            ctx.request.session['user'] = login
            ctx.response.status_code = 302
            ctx.response.location = ctx.adapter.build('user_tag',
                                                      {'user': login})
        else:
            ctx.values['error'] = True

@bp.route('/logout')
def get_logout():
    session['user'] = None
    return redirect(url_for('index'))
