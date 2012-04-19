from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

meta = MetaData()
meta.bind = db.session.bind

user = Table('user', meta,
             Column('id', Integer, primary_key=True),
             Column('name', String))
user.create()

open_id = Table('open_id', meta,
                Column('openid', String, primary_key=True),
                Column('user', Integer, ForeignKey('user.id'), nullable=False))
open_id.create()
