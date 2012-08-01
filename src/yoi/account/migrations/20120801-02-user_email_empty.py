db.session.execute('''
    update "user" set email = null where email = ''
''')
db.session.commit()
