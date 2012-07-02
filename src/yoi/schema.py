from collections import namedtuple
from flask import url_for
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from werkzeug import cached_property

from yoi.app import app

# Member is a synthetic object describing the members of events.
Member = namedtuple('Member', 'id name email amount user_id')

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
    def url_for(self):
        return url_for('event',
                       external_id=self.external_id,
                       slug='hello-world')

    @cached_property
    def members(self):
        rows = (app.db.session
                    .query(Person.id, Person.name,
                           app.db.User.name, app.db.User.email, app.db.User.id)
                    .filter(Person.event == self.id)
                    .filter(app.db.User.id == Person.user)
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
