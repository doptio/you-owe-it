from __future__ import unicode_literals, division

from flask import g, request, url_for, redirect, flash
from flaskext.genshi import render_response
from flaskext.wtf import Form, TextField, Required

from yoi.app import app

@app.route('/')
def index():
    return render_response('index.html')

@app.route('/home')
def home():
    return render_response('home.html')

class UserSettingsForm(Form):
    name = TextField('name', validators=[Required()])

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form = UserSettingsForm(obj=g.user)

    if form.validate_on_submit():
        form.populate_obj(g.user)
        app.db.session.commit()

        flash('settings saved')
        return redirect(url_for('home'))

    if form.errors:
        flash('settings not saved', 'alert')

    return render_response('settings.html', {'form': form})

@app.route('/journal')
def journal():
    return render_response('journal.html')

@app.route('/new-entry')
def new_entry():
    return render_response('new-entry.html')
