db.session.execute('''
    alter table entry
        drop constraint entry_amount_check;
''')
db.session.commit()
