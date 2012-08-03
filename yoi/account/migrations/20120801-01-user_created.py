db.session.execute('''
    alter table "user"
    add column created timestamp
''')
db.session.execute('''
    update "user" set created = '1979-07-07'
''')
db.session.execute('''
    alter table "user" alter column created set not null
''')
db.session.commit()
