from __future__ import unicode_literals, division

from selector import Selector

from dweeb.framework import page, with_database
from dweeb.resources import static_app
from dweeb.template import with_template

@page
@with_template('index.html')
def get_index(request):
    pass

app = Selector()
app.add('/static/|', GET=static_app, HEAD=static_app)
app.add('/', GET=get_index)
