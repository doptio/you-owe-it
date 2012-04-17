from __future__ import unicode_literals, division

from flask import Flask, request
from flaskext.genshi import Genshi, render_response

from dweeb.middleware import wrap_application

app = Flask(__name__)
genshi = Genshi(app)
app.wsgi_app = wrap_application(app.wsgi_app)

@app.route('/', methods=['GET'])
def get_index():
    return render_response('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=4000)
