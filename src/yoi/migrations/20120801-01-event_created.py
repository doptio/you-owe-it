db.session.execute('''
    alter table "event"
    add column created timestamp
''')
db.session.execute('''
    update "event" set created = '1979-07-07'
''')
db.session.execute('''
    alter table "event" alter column created set not null
''')
db.session.commit()
