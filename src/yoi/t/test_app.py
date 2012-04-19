from __future__ import unicode_literals, division

from contextlib import contextmanager
from mock import patch
from openid.consumer.consumer import SUCCESS

from dweeb.testing import setup_module, assert_eq

from yoi.site import app

def test_index():
    resp = client.get('/')
    assert_eq(resp.status_code, 200)

### FIXME - These belong in the dweeb.account package.

def create_user():
    user = app.db.User(name='toor')
    app.db.session.add(user)
    openid = app.db.OpenId(user=user, openid='http://uowe.it/root')
    app.db.session.add(openid)
    app.db.session.commit()
    return user

@contextmanager
def fake_openid():
    with patch('dweeb.account.user.make_consumer') as mock:
        result = mock.return_value.complete.return_value
        result.status = SUCCESS
        result.identity_url = 'http://uowe.it/root'
        result.getSignedNS.return_value = {'nickname': 'God'}

        yield mock


def test_login_new_user():
    with fake_openid():
        resp = client.get('/openid-return')
        assert_eq(resp.status_code, 302)
        assert_eq(resp.location, 'http://localhost/register')

    assert_eq(app.db.session.query(app.db.OpenId.openid).all(),
              [('http://uowe.it/root',)])


def test_register():
    user = create_user()

    with client.session_transaction() as sess:
        sess['user_id'] = user.id

    resp = client.get('/register')
    assert_eq(resp.status_code, 200)

    resp = client.post('/register', data={
        'name': 'Odin',
    })
    assert_eq(resp.status_code, 302)
    assert_eq(resp.location, 'http://localhost/')


def test_login_exists():
    create_user()

    with fake_openid():
        resp = client.get('/openid-return')
        assert_eq(resp.status_code, 302)
        assert_eq(resp.location, 'http://localhost/')

    assert_eq(app.db.session.query(app.db.OpenId.openid).all(),
              [('http://uowe.it/root',)])
