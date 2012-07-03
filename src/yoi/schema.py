from collections import namedtuple
from flask import url_for
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
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
