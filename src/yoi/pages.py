from __future__ import unicode_literals, division

from flask import g, request, url_for, redirect, flash
from flaskext.genshi import render_response
from flaskext.wtf import Form, TextField, Required, Optional, Email, Length, \
                         FieldList
from random import randrange
from sqlalchemy import sql

from yoi.app import app
from yoi.schema import Event, Person

@app.route('/')
def index():
    return render_response('index.html')

@app.route('/tour')
def tour():
    return render_response('tour.html')

@app.route('/home')
def home():
    events = (app.db.session
                .query(Event)
                .filter(Event.id.in_(sql.select([Person.event],
                                                Person.user == g.user.id)))
                .order_by(Event.name)
                .all())
    return render_response('home.html', {'events': events})

class UserSettingsForm(Form):
    name = TextField('name', validators=[
        Required(),
        Length(min=3, max=15),
    ])
    email = TextField('e-mail', validators=[
        Optional(),
        Email(),
        Length(max=30),
    ])

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

class NewEventForm(Form):
    name = TextField('name', validators=[
        Required(),
        Length(min=3, max=20),
    ])
    people = FieldList(TextField('name', validators=[Optional()]))

def random_identifier():
    # FIXME - disallow identifiers that do not start with a number?
    # FIXME - check that the identifier does not exist already!
    return '%06x' % randrange(0x100000, 0xffffff)

def create_event(form):
    event = Event(name=form.name.data)
    event.external_id = random_identifier()
    app.db.session.add(event)
    app.db.session.flush()  # need event.id

    app.db.session.add(Person(event=event.id,
                              name=g.user.name,
                              user=g.user.id))
    for name in form.people.data:
        app.db.session.add(Person(event=event.id, name=name))

    return event

@app.route('/new-event', methods=['GET', 'POST'])
def new_event():
    form = NewEventForm()

    if form.validate_on_submit():
        event = create_event(form)
        app.db.session.commit()

        flash('event created')
        return redirect(event.url_for)

    if form.errors:
        flash('event not created', 'alert')

    return render_response('new-event.html', {'form': form})

@app.route('/<external_id>/<slug>')
def event(external_id, slug):
    event = Event.find(external_id)
    return render_response('event.html', {'event': event})
