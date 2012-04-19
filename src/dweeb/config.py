import os

here = os.path.dirname(__file__)

default_logging_config = os.path.join(here, 'logging.ini')
logging_config = os.environ.get('LOGGING_CONFIG', default_logging_config)

# psycopg2 is stupid and insists on us telling it stuff libpq is perfectly
# capable of figuring our for it, so we put a reasonable default database name
# into our default DB URL. Silly rabbits.
default_db_url = 'postgresql:///' + os.environ['LOGNAME']
db_url = os.environ.get('DATABASE_URL', default_db_url)

testing = os.environ.get('TESTING') == 'true'
in_production = os.environ.get('ENVIRONMENT') == 'production'
use_debugger = not (testing or in_production)
always_secure = in_production

database_url = os.environ.get('DATABASE_URL', 'postgresql://')

if in_production:
    secret = os.environ['SECURE_COOKIE_SECRET']
else:
    secret = b'\xd4\x94\x17[[g\xb7\xb6\xf9\x81[\xa3\xafw%\x87\xbf0=\x80'

del os
