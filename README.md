You Owe It!
~~~~~~~~~~~

Creating a Development Environment
==================================

1. Clone this repository.
1 1/2. Install packages::

    sudo apt-get install python-dev build-essentials libxml2-dev libxslt-dev \
        libpq-dev postgresql

2. Create a virtualenv::

    virtualenv --no-site-packages --prompt '(yoi) ' venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -r development-requirements.txt
    python setup.py develop

3. Create a database (make sure the environment variable `${DATABASE_URL}`
   points somewhere SQLAlchemy understands, or that you have a PostgreSQL
   database with the same name as your login)::

    bin/manage.py migrate
