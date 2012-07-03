from __future__ import unicode_literals, division

from datetime import date
from flask import g, request, url_for, redirect, flash, jsonify
from flaskext.genshi import render_response
from random import randrange
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from yoi.app import app
from yoi.schema import Event, Person, Entry, EntryVictim
from yoi.wtf import Form, TextField, Required, Optional, Email, Length, \
                    Field, IntegerField, BooleanField, \
                    DecimalField, NumberRange, DateField, ListOf

@app.route('/')
def index():
    return render_response('index.html')

@app.route('/tour')
def tour():
    return render_response('tour.html')

@app.route('/home')
def home():
    return render_response('home.html', {'events': Event.for_user(g.user.id)})

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
        try:
            with app.db.session.begin_nested():
                form.populate_obj(g.user)
            app.db.session.commit()

            flash('settings saved')
            return redirect(url_for('home'))

        except IntegrityError:
            form.email.errors.append('Email already taken')

    if form.errors:
        flash('settings not saved', 'alert')

    return render_response('settings.html', {'form': form})

class NewEventForm(Form):
    name = TextField('name', validators=[
        Required(),
        Length(min=3, max=20),
    ])
    people = ListOf(TextField('name', validators=[Optional()]))

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
        if not name:
            continue
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

class EmptyForm(Form):
    'I am an empty form. Use me to generate CSRF tokens.'
    pass

@app.route('/<external_id>/<slug>/')
def event(external_id, slug):
    event = Event.find(external_id)
    return render_response('event.html', {
        'event': event,
        'form': EmptyForm(),
    })

class JoinEventForm(Form):
    person = IntegerField('person', validators=[Optional()])

@app.route('/<external_id>/<slug>/join', methods=['POST'])
def join_event(external_id, slug):
    form = JoinEventForm()

    if form.validate_on_submit():
        event = Event.find(external_id)
        if form.person.data:
            person = Person.get(form.person.data)
            if person.event != event.id:
                request.log.info('person.event != event.id')
                raise BadRequest()
            if person.user:
                request.log.info('person.user != None')
                raise BadRequest()
            person.user = g.user.id

        else:
            person = Person(event=event.id, name=g.user.name, user=g.user.id)
            app.db.session.add(person)

        app.db.session.commit()

        return jsonify(success=True)

    request.log.info('form not valid: %r', form.errors)
    raise BadRequest()

class NewEntryForm(Form):
    payer = IntegerField(validators=[Required()])
    date = DateField(default=date.today, validators=[Required()])
    description = TextField(validators=[Required()])
    manual_entry = BooleanField()
    amount = DecimalField(validators=[Required(), NumberRange(min=1)])

    victims = ListOf(IntegerField())
    shares = ListOf(DecimalField())

    def validate_payer(self, field):
        if field.data not in self.valid_people:
            raise ValueError('unknown person')

    def post_validate(self, form, validation_stopped):
        if len(form.victims.data) != len(form.shares.data):
            raise ValueError('len(victims) != len(shares)')

        for victim in form.victims.data:
            if victim not in form.valid_people:
                raise ValueError('unknown person')

def create_entry(event, form):
    entry = Entry()
    entry.event = event.id
    entry.payer = form.payer.data
    entry.date = form.date.data
    entry.description = form.description.data
    entry.manual_entry = form.manual_entry.data
    entry.amount = int(form.amount.data * 100)
    app.db.session.add(entry)
    app.db.session.flush()

    for victim, share in zip(form.victims.data, form.shares.data):
        share = int(share * 100)
        if not share:
            continue
        app.db.session.add(EntryVictim(entry=entry.id,
                                       victim=victim,
                                       share=share))

@app.route('/<external_id>/<slug>/entry/', methods=['GET', 'POST'])
def new_entry(external_id, slug):
    event = Event.find(external_id)

    request.log.debug('data: %r', request.form)
    form = NewEntryForm()
    # used by field validators -- FIXME is this kosher?
    form.valid_people = [person.person_id for person in event.members]
    if form.validate_on_submit():
        create_entry(event, form)
        app.db.session.commit()

        flash('entry added')
        return redirect(event.url_for)

    if form.errors:
        request.log.debug('form errors: %r', form.errors)
        flash('entry not added', 'alert')

    return render_response('new-entry.html', {'form': form, 'event': event})
