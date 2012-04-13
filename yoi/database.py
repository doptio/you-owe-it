from __future__ import unicode_literals, division

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

from dweeb.database import DatabaseError

class NoSuchUser(DatabaseError):
    pass

class UserExists(DatabaseError):
    pass

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    created = Column(DateTime, nullable=False)

    @classmethod
    def create(cls, session, login):
        user = User()
        user.login = login
        user.created = datetime.utcnow()
        session.add(user)

        try:
            session.flush()
        except IntegrityError:
            raise UserExists(login)

        return user

    @classmethod
    def get(cls, session, id):
        try:
            return session.query(User).get(id)
        except NoResultFound:
            raise NoSuchUser(id)

    @classmethod
    def find(cls, session, login):
        try:
            return session.query(User).filter_by(login=login).one()
        except NoResultFound:
            raise NoSuchUser(login)

    @classmethod
    def for_request(cls, request):
        return cls.get(request.cnx, request.session['user_id'])

'''
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
'''
