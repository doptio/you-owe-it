from __future__ import unicode_literals, division

from yoi.app import app
from yoi import pages
from yoi import authentication

if __name__ == '__main__':
    app.run('0.0.0.0', port=4000)
