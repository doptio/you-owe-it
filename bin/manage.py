#!/usr/bin/env python

from flask.ext.migrate import Migrate
from flask.ext.script import Manager

from yoi.site import app

app.extensions['script'] = manager = Manager(app)
migrate = Migrate(app)

if __name__ == "__main__":
    manager.run()
