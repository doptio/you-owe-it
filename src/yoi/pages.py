from flask import request
from flaskext.genshi import render_response

from yoi.app import app

@app.route('/')
def index():
    return render_response('index.html')

@app.route('/home')
def home():
    return render_response('home.html')

@app.route('/journal')
def journal():
    return render_response('journal.html')

@app.route('/new-entry')
def new_entry():
    return render_response('new-entry.html')
