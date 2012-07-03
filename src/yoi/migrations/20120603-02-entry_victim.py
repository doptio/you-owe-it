from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, \
                       CheckConstraint, Boolean, UniqueConstraint

meta = MetaData()
meta.bind = db.session.bind

event = Table('event', meta, Column('id', Integer, primary_key=True))
person = Table('person', meta, Column('id', Integer, primary_key=True))
entry = Table('entry', meta, Column('id', Integer, primary_key=True))

entry_victim = Table('entry_victim', meta,
              Column('id', Integer, primary_key=True),
              Column('entry', Integer, ForeignKey('entry.id'),
                     nullable=False),
              Column('victim', Integer, ForeignKey('person.id'),
                     nullable=False),
              Column('share', Integer, CheckConstraint('share > 0'),
                     nullable=False),
              UniqueConstraint('entry', 'victim'))
entry_victim.create()
