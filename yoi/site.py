from __future__ import unicode_literals, division

from dweeb.middleware import wrap_application
from dweeb.resources import dweeb_resources

from yoi.pages import app

app = wrap_application(app)

resources = {}
resources.update(dweeb_resources)
