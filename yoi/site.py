from __future__ import unicode_literals, division

from dweeb.middleware import gzipper, loggy
from dweeb.config import use_debugger, static_files

from yoi.pages import app

app = gzipper(app)
app = loggy(app)

if use_debugger:
    from werkzeug.debug import DebuggedApplication
    app = DebuggedApplication(app, evalex=True)

if static_files:
    from werkzeug.wsgi import SharedDataMiddleware
    app = SharedDataMiddleware(app, static_files)
