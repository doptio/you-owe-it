from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, \
                       UniqueConstraint

meta = MetaData()
meta.bind = db.session.bind

user = Table('user', meta, Column('id', Integer, primary_key=True))
event = Table('event', meta, Column('id', Integer, primary_key=True))

person = Table('person', meta,
               Column('id', Integer, primary_key=True),
               Column('event', Integer, ForeignKey('event.id'),
                      nullable=False),
               Column('user', Integer, ForeignKey('user.id'),
                      nullable=True),
               Column('name', String),
               UniqueConstraint('event', 'user'))
person.create()
