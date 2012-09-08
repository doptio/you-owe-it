db.session.execute('''
    alter table "event"
    add column closed timestamp
''')
db.session.commit()
