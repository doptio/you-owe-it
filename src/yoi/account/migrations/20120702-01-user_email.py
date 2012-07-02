db.session.execute('''
    alter table "user"
    add column email varchar unique
''')
db.session.commit()
