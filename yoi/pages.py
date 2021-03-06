from __future__ import unicode_literals, division

from datetime import date, datetime
from flask import g, request, url_for, redirect, flash, jsonify
from flaskext.genshi import render_response
from random import randrange
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, NotFound

from yoi.app import app
from yoi.schema import Event, Person, Entry, EntryVictim
from yoi.wtf import Form, TextField, Required, Optional, AnyOf, Email, \
                    Length, Field, IntegerField, BooleanField, \
                    DecimalField, NumberRange, DateField, ListOf, \
                    FileField

@app.route('/')
def index():
    if g.user:
        return redirect(url_for('home'))
    return render_response('index.html')

@app.route('/tour')
def tour():
    return render_response('tour.html')

@app.route('/home')
def home():
    show_closed = bool(request.args.get('show-closed'))
    events = Event.for_user(g.user.id, show_closed)
    return render_response('home.html', {
        'events': events,
        'show_closed': show_closed,
    })

def clear_if_empty(v):
    if not v:
        return None
    else:
        return v

class UserSettingsForm(Form):
    name = TextField('name',
                     validators=[Required(), Length(min=1, max=42)])
    email = TextField('e-mail',
                      validators=[Optional(), Email(), Length(max=42)],
                      filters=[clear_if_empty])

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
            request.log.warn('IntegrityError saving user %d <- %r',
                             g.user.id, request.form, exc_info=True)
            form.email.errors.append('Email already taken')

    if form.errors:
        flash('settings not saved', 'alert')

    return render_response('settings.html', {'form': form})

class NewEventForm(Form):
    name = TextField('name', validators=[Required(), Length(min=1, max=42)])
    people = ListOf(TextField('name',
                              validators=[Optional(), Length(min=1, max=42)]))

def random_identifier():
    # FIXME - disallow identifiers that do not start with a number?
    # FIXME - check that the identifier does not exist already!
    return '%06x' % randrange(0x100000, 0xffffff)

def create_event(form):
    event = Event(name=form.name.data, created=datetime.utcnow())
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

class EventForm(Form):
    action = TextField('action',
                       validators=[Required(),
                                   AnyOf(['close', 'reopen',
                                          'join', 'leave',
                                          'remove-person'])])
    person = IntegerField('person', validators=[Optional()])

    def update_event(self, event):
        if self.action.data == 'close':
            event.closed = datetime.utcnow()
        elif self.action.data == 'reopen':
            event.closed = None
        elif self.action.data == 'join':
            join_event(event, g.user, self.person.data)
        elif self.action.data == 'leave':
            leave_event(event, g.user)
        elif self.action.data == 'remove-person':
            person = Person.get(self.person.data)
            person.removed = datetime.utcnow()
            person.user = None
        else:
            raise ValueError('Huh?!')

def join_event(event, user, person_id):
    if person_id:
        person = Person.get(person_id)
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

def leave_event(event, user):
    person = (app.db.session
                .query(Person)
                .filter_by(event=event.id, user=user.id)
                .one())
    person.user = None

@app.route('/<external_id>/<slug>/', methods=['GET', 'POST'])
def event(external_id, slug):
    event = Event.find_or_404(external_id)

    form = EventForm()
    if form.validate_on_submit():
        form.update_event(event)
        app.db.session.commit()

    if request.is_xhr:
        if form.errors:
            return bad_request()
        return jsonify(success=True)
    else:
        return render_response('event.html', {
            'event': event,
            'form': EmptyForm(),
        })

@app.route('/<external_id>/<slug>/entry/')
def all_entries(external_id, slug):
    event = Event.find_or_404(external_id)
    return render_response('all-entries.html', {'event': event})

def requested_entry(external_id, entry_id):
    event = Event.find_or_404(external_id)
    try:
        entry, = [entry
                  for entry in event.all_entries
                  if entry.id == entry_id]
    except ValueError:
        raise NotFound()
    return event, entry

@app.route('/<external_id>/<slug>/entry/<int:entry_id>')
def entry(external_id, slug, entry_id):
    event, entry = requested_entry(external_id, entry_id)
    return render_response('entry.html', {
        'form': EmptyForm(),
        'event': event,
        'entry': entry,
    })

@app.route('/<external_id>/<slug>/entry/<int:entry_id>/delete',
           methods=['POST'])
def delete_entry(external_id, slug, entry_id):
    if not EmptyForm().validate_on_submit():
        return 'Bad request', 400

    event, entry = requested_entry(external_id, entry_id)

    app.db.session.query(EntryVictim).filter_by(entry=entry.id).delete()
    app.db.session.query(Entry).filter_by(id=entry.id).delete()
    app.db.session.commit()

    return redirect(event.url_for)

class AddPeopleForm(Form):
    people = ListOf(TextField(validators=[Length(min=1, max=42)]))

@app.route('/<external_id>/<slug>/add-people', methods=['POST'])
def add_people(external_id, slug):
    event = Event.find_or_404(external_id)
    form = AddPeopleForm()

    if form.validate_on_submit():
        for person in form.people.data:
            app.db.session.add(Person(event=event.id, name=person))
        app.db.session.commit()

        return jsonify(success=True)

    request.log.info('form not valid: %r', form.errors)
    raise BadRequest()

class NewEntryForm(Form):
    payer = IntegerField(validators=[Required()])
    date = DateField(default=date.today, validators=[Required()])
    description = TextField(validators=[Required(), Length(min=1, max=100)])
    manual_entry = BooleanField()
    amount = DecimalField(validators=[Required()])

    victims = ListOf(IntegerField())
    shares = ListOf(DecimalField())

    def validate_payer(self, field):
        if field.data not in self.valid_people:
            raise ValueError('unknown person')

    def validate(self):
        super(Form, self).validate()

        # Remove victims with 0 shares.
        victims = [(victim, share)
                   for victim, share in zip(self.victims.data,
                                            self.shares.data)
                   if share]
        if not victims:
            self.victims.errors.append('At least one victim is required')
        else:
            self.victims.data, self.shares.data = zip(*victims)

        # Sanity check input.
        if len(self.victims.data) != len(self.shares.data):
            raise ValueError('len(victims) != len(shares)')

        for victim in self.victims.data:
            if victim not in self.valid_people:
                raise ValueError('unknown person')

        return not self.errors

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
        app.db.session.add(EntryVictim(entry=entry.id,
                                       victim=victim,
                                       share=int(share * 100)))

@app.route('/<external_id>/<slug>/entry/new', methods=['GET', 'POST'])
def new_entry(external_id, slug):
    event = Event.find_or_404(external_id)

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

def import_csv(event, data):
    count = 0
    for line in data:
        count += 1

        try:
            pieces = line.strip().decode('utf-8').split(';', 4)
            date, amount, payer, victims, description = pieces
        except Exception:
            raise ValueError('Bad CSV line: %r' % line)

        entry = Entry()
        entry.event = event.id
        entry.payer = event.get_or_create_person(payer).id
        entry.date = datetime.strptime(date, '%d-%m-%Y')
        entry.description = description
        entry.manual_entry = False
        entry.amount = int(float(amount) * 100)
        app.db.session.add(entry)
        app.db.session.flush()

        for victim in victims.split(','):
            victim, shares = victim.split('=')
            victim = event.get_or_create_person(victim).id
            shares = int(shares)
            app.db.session.add(EntryVictim(entry=entry.id,
                                           victim=victim,
                                           share=shares))

    return count

class ImportForm(Form):
    csv_file = FileField('CSV File',
                         validators=[Required()])

@app.route('/<external_id>/<slug>/import', methods=['GET', 'POST'])
def import_entries(external_id, slug):
    event = Event.find_or_404(external_id)

    form = ImportForm()
    if form.validate_on_submit():
        try:
            count = import_csv(event, request.files['csv_file'])
        except ValueError, e:
            request.log.warn('Bad CSV file', exc_info=True)
            form.errors['csv_file'] = form.csv_file.errors = [e.args[0]]
        else:
            app.db.session.commit()

            flash('%d entries imported' % count)
            return redirect(event.url_for)

    if form.errors:
        request.log.debug('form errors: %r', form.errors)
        flash('there were errors', 'alert')

    return render_response('import-entries.html',
                           {'form': form, 'event': event})

@app.route('/admin/')
def admin_index():
    return render_response('admin/index.html')

@app.route('/admin/user/')
def admin_list_users():
    users = (app.db.session
                .query(app.db.User)
                .order_by(app.db.User.created.desc(),
                          app.db.User.id.desc())
                .all())
    return render_response('admin/users.html', {'users': users})

@app.route('/admin/event/')
def admin_list_events():
    events = (app.db.session
                .query(Event)
                .order_by(Event.created.desc(),
                          Event.id.desc())
                .all())
    return render_response('admin/events.html', {'events': events})

@app.route('/admin/uncaught-exception')
def admin_uncaught_exception():
    raise AssertionError('2 + 2 != 5')

@app.route('/admin/env')
def admin_env():
    return render_response('admin/env.html', {'env': request.environ})
