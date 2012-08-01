from collections import namedtuple, defaultdict, OrderedDict as ordereddict
from flask import url_for
from sqlalchemy import sql
from sqlalchemy import Column, Integer, String, \
                       CheckConstraint, ForeignKey, UniqueConstraint
import translitcodec  # imported to get the translit/long encoding
from werkzeug import cached_property

from yoi.app import app

import re

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))

# Member is a synthetic object describing the members of events.
Member = namedtuple('Member', 'person_id name email amount user_id')

class Event(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    created = app.db.Column(app.db.DateTime, nullable=False)
    external_id = app.db.Column(app.db.String, nullable=False, unique=True)
    name = app.db.Column(app.db.String)

    @classmethod
    def get(cls, event_id):
        return app.db.session.query(cls).get(event_id)

    @classmethod
    def find(cls, external_id):
        return (app.db.session
                    .query(cls)
                    .filter_by(external_id=external_id)
                    .one())

    @classmethod
    def for_user(cls, user_id):
        return (app.db.session
                    .query(Event)
                    .filter(Event.id.in_(
                                sql.select([Person.event],
                                           Person.user == user_id)))
                    .order_by(Event.name)
                    .all())

    @property
    def slug(self):
        # slugify can return an empty string, if the given text is all asian
        # for example, so we have 'lorem-ipsum' as a fallback.
        return slugify(self.name) or 'lorem-ipsum'

    @property
    def url_for(self):
        return url_for('event',
                       external_id=self.external_id,
                       slug=self.slug)

    @cached_property
    def members(self):
        rows = (app.db.session
                    .query(Person.id, Person.name,
                           app.db.User.name, app.db.User.email,
                           app.db.User.id)
                    .outerjoin(app.db.User)
                    .filter(Person.event == self.id)
                    .order_by(Person.name))
        return [Member(row[0], row[1] or row[2], row[3], 0.0, row[4])
                for row in rows]

    @cached_property
    def all_entries(self):
        entry_and_victim = (
                app.db.session
                    .query(Entry, EntryVictim)
                    .filter(Entry.event == self.id,
                            EntryVictim.entry == Entry.id)
                    .order_by(Entry.date.desc(), Entry.id.desc())
                    .all())

        # Reshape (entry, victim) list into a list of (entry, victims).
        entries = ordereddict()
        for entry, victim in entry_and_victim:
            if entry.id not in entries:
                entry.victims = []
                entries[entry.id] = entry
            entries[entry.id].victims.append(victim)

        return entries.values()

    @cached_property
    def person_total(self):
        # Calculate the total worth of each person in the event.
        person_total = defaultdict(int)
        for entry in self.all_entries:
            shares_total = sum(victim.share for victim in entry.victims)
            person_total[entry.payer] += entry.amount
            for victim in entry.victims:
                amount = entry.amount * victim.share / shares_total
                person_total[victim.victim] -= amount

        return person_total

    @cached_property
    def user_total(self):
        return dict((person.user_id, self.person_total[person.person_id])
                    for person in self.members
                    if person.user_id)

    @cached_property
    def last_changed(self):
        if not self.all_entries:
            return
        return self.all_entries[0].date

class Person(app.db.Model):
    '''People are the association between events and user.

    They do not have to correspond to any user, since we want to allow victims
    that are not associated with any user.'''

    id = app.db.Column(app.db.Integer, primary_key=True)
    event = app.db.Column(app.db.Integer, ForeignKey('event.id'),
                          nullable=False)
    user = app.db.Column(app.db.Integer, ForeignKey('user.id'),
                         nullable=True)
    name = app.db.Column(app.db.String, nullable=False)

    __table_args__ = (
        UniqueConstraint('event', 'user'),
    )

    @classmethod
    def get(cls, id):
        return app.db.session.query(cls).get(id)

class Entry(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    date = app.db.Column(app.db.Date, nullable=False)
    event = app.db.Column(app.db.Integer, ForeignKey('event.id'),
                          nullable=False)
    payer = app.db.Column(app.db.Integer, ForeignKey('person.id'),
                          nullable=False)
    description = app.db.Column(app.db.String, nullable=False)

    # We don't need manual_entry in the backend, but we store it so the
    # frontend 'edit entry' UI can recreate the original entry state.
    manual_entry = app.db.Column(app.db.Boolean, nullable=False)
    # Amounts are stored with cents precision, so we store them as integers.
    amount = app.db.Column(app.db.Integer,
                           CheckConstraint('amount > 0'), nullable=False)

class EntryVictim(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)

    entry = app.db.Column(app.db.Integer, ForeignKey('entry.id'),
                          nullable=False)
    victim = app.db.Column(app.db.Integer, ForeignKey('person.id'),
                           nullable=False)
    share = app.db.Column(app.db.Integer,
                          CheckConstraint('share > 0'), nullable=False)

    # FIXME - It would be great with a constraint ensuring that
    # `entry.event == victim.event`.

    __table_args__ = (
        UniqueConstraint('entry', 'victim'),
    )
