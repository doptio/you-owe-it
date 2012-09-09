db.session.execute('''
    alter table "person"
    add column removed timestamp
''')
db.session.commit()
