from glob import glob
from simpletal import simpleTAL, simpleTALES
from selector import Selector
from yaro import Request
from cStringIO import StringIO

from database import load_database
from database import save_database

import os
import re
import time
import datetime

here = os.path.dirname(__file__)
database_path = os.path.join(here, 'dbs')
template_root = os.path.join(here, 'templates')
macro_templates = glob(os.path.join(template_root, 'macros', '*'))
re_good_database = re.compile('^[a-z0-9-]+$')

response_headers = [
    ('Content-Type', 'text/html; charset=utf-8'),
]

def wsgi_wrap(handler):
    def wrapped(environ, start_response):
        start_response('200 Ok', response_headers)
        args, kwargs = environ['wsgiorg.routing_args']
        return handler(Request(environ, start_response), *args, **kwargs)

    return wrapped

def load_macros():
    macros = {}
    for template_path in macro_templates:
        tpl = simpleTAL.compileHTMLTemplate(open(template_path, 'r'))
        macros.update(tpl.macros)
    return macros

def find_template(template_names):
    for template_name in template_names:
        template_path = os.path.join(template_root, template_name + '.html')
        if os.path.exists(template_path):
            return template_path
    else:
        raise AssertionError('No template found; %r' % template_names)

def render_to_response(template_names, bindings):
    template_path = find_template(template_names)

    tpl = simpleTAL.compileHTMLTemplate(open(template_path, 'r'))
    ctx = simpleTALES.Context(allowPythonPath=True)
    ctx.globals.update(bindings)
    ctx.globals['macros'] = load_macros()

    out = StringIO()
    tpl.expand(ctx, out, outputEncoding='utf-8')

    return [out.getvalue()]

@wsgi_wrap
def index(request):
    return render_to_response(['index'], {
        'databases': filter(re_good_database.match,
                            os.listdir(database_path)),
    })

@wsgi_wrap
def db_index(request, db_name):
    db = load_database(os.path.join(database_path, db_name))

    udlagt = {}
    gaeld = {}

    for row in db:
        total_streger = 0
        for offer, streger in row.victims:
            total_streger = total_streger + streger
        for offer, streger in row.victims:
            gaeld[offer] = gaeld.get(offer, 0.0) + row.amount * streger / total_streger
        udlagt[row.spender] = udlagt.get(row.spender, 0.0) + row.amount

    template_names = ['db/%s/index' % db_name, 'db/index']
    return render_to_response(template_names, {
        'database': db,
        'udlaeg': [ udlagt.get(p, 0.0) for p in db.people ],
        'forbrug': [ gaeld.get(p, 0.0) for p in db.people ],
        'total': [ udlagt.get(p, 0.0) - gaeld.get(p, 0.0) for p in db.people ],
        'today': datetime.date.today().strftime('%d-%m'),
    })

@wsgi_wrap
def db_poster(request, db_name):
    db = load_database(os.path.join(database_path, db_name))
    return render_to_response(['db/poster'], { 'database': db })

@wsgi_wrap
def db_opret(request, db_name):
    path = os.path.join(database_path, db_name)
    db = load_database(path)

    dato = request.form['dato']
    fields = dato.split('-')
    if len(fields) == 2:
        year = time.localtime()[0]
        dato = datetime.date(year, int(fields[1]), int(fields[0]))
    else:
        fields = [ int(it) for it in fields ]
        fields.reverse()
        dato = datetime.date(*fields)
    
    udlaeg = float(request.form['udlaeg'])

    udlaegger = request.form['udlaegger'].decode('utf-8')
    if not udlaegger in db.people:
        raise AssertionError, 'unknown person'
    
    kommentar = request.form['kommentar'].decode('utf-8')

    ofrer = []
    for person in db.people:
        streger = int(request.form.get(person + '-streger', '0'))
        if streger:
            offer = person, streger
            ofrer.append(offer)
    if not ofrer:
        raise AssertionError, 'no victims'

    row = dato, udlaeg, udlaegger, ofrer, kommentar

    db.insert(row)
    save_database(path, db)

    return render_to_response(['db/opret'], {})

pages = Selector()
pages.parser.patterns['slug'] = r'[a-z0-9-]+'
pages.add('/', GET=index)
pages.add('/{db_name:slug}/', GET=db_index)
pages.add('/{db_name:slug}/poster/', GET=db_poster)
pages.add('/{db_name:slug}/opret/', POST=db_opret)
