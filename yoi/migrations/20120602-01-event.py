from sqlalchemy import MetaData, Table, Column, Integer, String

meta = MetaData()
meta.bind = db.session.bind

event = Table('event', meta,
              Column('id', Integer, primary_key=True),
              Column('external_id', String, nullable=False, unique=True),
              Column('name', String))
event.create()
