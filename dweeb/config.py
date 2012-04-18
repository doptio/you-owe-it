import os

here = os.path.dirname(__file__)

default_logging_config = os.path.join(here, 'logging.ini')
logging_config = os.environ.get('LOGGING_CONFIG', default_logging_config)

in_production = os.environ.get('ENVIRONMENT') == 'production'
use_debugger = not in_production
always_secure = in_production

database_url = os.environ.get('DATABASE_URL', 'postgresql://')

if in_production:
    secret = os.environ['SECURE_COOKIE_SECRET']
else:
    secret = b'\xd4\x94\x17[[g\xb7\xb6\xf9\x81[\xa3\xafw%\x87\xbf0=\x80'

del os
