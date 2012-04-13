from __future__ import unicode_literals, division

import datetime
import os.path
import time

class Row:
    def __init__(self, (dato, udlaeg, udlaegger, ofrer, kommentar)):
        self.date = dato
        self.amount = udlaeg
        self.spender = udlaegger
        self.victims = ofrer
        self.comment = kommentar

class Database:
    def __init__(self, people, rows):
        self.people = people
        self.rows = rows
        self.changed = 0

    def __iter__(self):
        return iter(self.rows)

    def insert(self, row):
        self.changed = 1
        self.rows.append(Row(row))
        self.rows.sort(lambda a, b: cmp(a.date, b.date))

def parse_date(dato):
    day, mon, year = [ int(it) for it in dato.split('-') ]
    return datetime.date(year, mon, day)

def load_database(path):
    file = open(path)

    people = file.readline().strip().split()
    rows = []
    for line in file:
        line = line.decode('utf-8').rstrip()
        dato, udlaeg, udlaegger, ofrer, kommentar = line.split(None, 4)
        dato = parse_date(dato)
        streg_ofrer = ofrer.split(',')
        ofrer = [o.split('=') for o in streg_ofrer]
        ofrer = [(o, int(s)) for o, s in ofrer]
        udlaeg = float(udlaeg)
        row = Row((dato, udlaeg, udlaegger, ofrer, kommentar))
        rows.append(row)

    db = Database(people, rows)
    db.name = os.path.basename(path)
    return db

def save_database(path, database):
    file = open(path, 'w')
    file.write(' '.join(database.people) + '\n')
    for row in database:
        streg_ofrer = ['%s=%d' % (o, s) for o, s in row.victims]
        ofrer = ','.join(streg_ofrer)

        line = '%d-%d-%d %f %s %s %s' \
                % (row.date.day, row.date.month, row.date.year,
                   row.amount, row.spender, ofrer, row.comment)
        line = line.encode('utf-8')
        file.write(line + '\n')
    file.close()
