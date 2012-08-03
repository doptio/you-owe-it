from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, \
                       CheckConstraint, Boolean, Date

meta = MetaData()
meta.bind = db.session.bind

event = Table('event', meta, Column('id', Integer, primary_key=True))
person = Table('person', meta, Column('id', Integer, primary_key=True))

entry = Table('entry', meta,
              Column('id', Integer, primary_key=True),
              Column('date', Date, nullable=False),
              Column('event', Integer, ForeignKey('event.id'),
                     nullable=False),
              Column('payer', Integer, ForeignKey('person.id'),
                     nullable=False),
              Column('description', String, nullable=False),
              Column('manual_entry', Boolean, nullable=False),
              Column('amount', Integer, CheckConstraint('amount > 0'),
                     nullable=False))
entry.create()
