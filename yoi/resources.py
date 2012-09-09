from __future__ import unicode_literals, division

from flask import url_for, current_app
import os

from yoi.config import in_production

# Sane version of `url_for` for /static/ URLs (i.e. one we can actually hook
# into.)
def static_url(filename):
    if in_production or True:
        file_path = os.path.join(current_app.static_folder, filename)
        q = int(os.stat(file_path).st_mtime)
        return url_for('static', filename=filename, q=q)
    else:
        return url_for('static', filename=filename)
