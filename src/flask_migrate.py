from contextlib import contextmanager
from datetime import datetime
import os
import re
from sqlalchemy import Column, DateTime, String

script_re = re.compile(r'^\d{8}-\d\d-[a-z0-9-_]+\.(:?py|sql)$')

class AppliedChanges(object):
    __tablename__ = 'applied_changes'

    applied = Column(DateTime, nullable=False)
    name = Column(String, primary_key=True)


class Migrate(object):
    def __init__(self, app):
        # FIXME - Should not require `app` here. See
        # <http://flask.pocoo.org/docs/extensiondev/>.
        self.app = app
        self.init_app(app)

    def init_app(self, app):
        app.extensions['migrate'] = self

        # Register our commands.
        def migrate():
            self.migrate()
        app.extensions['script'].command(migrate)

        # Add our table to database.
        self.app.db.AppliedChanges = type('AppliedChanges',
                                          (AppliedChanges, self.app.db.Model),
                                          {})


    def all_scripts(self):
        modules = [('', self.app)]
        modules.extend((name + '/', bp)
                       for name, bp in self.app.blueprints.items())

        for prefix, module in modules:
            migrations = os.path.join(module.root_path, 'migrations')
            if not os.path.exists(migrations):
                continue

            for name in sorted(os.listdir(migrations)):
                if script_re.match(name):
                    yield prefix + name, os.path.join(migrations, name)

    def migrate(self):
        with context(self.app):
            Change = self.app.db.AppliedChanges
            Change.__table__.metadata.bind = self.app.db.session.bind
            Change.__table__.create(checkfirst=True)

            for name, path in self.all_scripts():
                if Change.query.filter_by(name=name).count():
                    continue

                self.app.db.session.add(Change(applied=datetime.utcnow(),
                                               name=name))
                print '%s . . .' % name
                self.apply_script(self.app.db, path)
                self.app.db.session.commit()

    def apply_script(self, db, path):
        with open(path) as file:
            if path.endswith('.sql'):
                cnx = db.session.connection()
                for statement in parse_sql_script(file):
                    cnx.execute(statement)

            elif path.endswith('.py'):
                code = compile(file.read(), path, 'exec')
                eval(code, {'db': db})


def parse_sql_script(f):
    return filter(None, [s.strip() for s in f.read().strip().split('\n\n')])


@contextmanager
def context(app):
    context = app.test_request_context()
    context.push()
    try:
        yield context
    finally:
        context.pop()
