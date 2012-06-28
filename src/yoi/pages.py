from flask import request
from flaskext.genshi import render_response

from yoi.app import app

@app.route('/')
def get_index():
    return render_response('index.html')

@app.route('/home')
def get_home():
    return render_response('home.html')

@app.route('/journal')
def get_journal():
    return render_response('journal.html')

@app.route('/new-entry')
def get_new_entry():
    return render_response('new-entry.html')
