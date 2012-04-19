'Sane logging defaults and thread-local context variables.'

from __future__ import unicode_literals, division

from contextlib import contextmanager
import logging
import logging.config
import os
import sys
import threading
from traceback import format_exception, format_exception_only

from dweeb.config import logging_config

def configure_logging():
    logging.config.fileConfig(logging_config,
                              # Please, don't be so retarded.
                              disable_existing_loggers=False)

formatters = [
    (lambda r: '[{}]'.format(r.levelname)),
    (lambda r: '[{}]'.format(r.name)),
    (lambda r: ' '.join('[{}: {}]'.format(key, val)
                        for key, val in vars(loggy_context).items())
               if loggy_context
               else None),
    (lambda r: (r.msg % r.args).strip()),
    (lambda r: '\n' + ''.join(format_exception(*r.exc_info))
               if r.exc_info
               else None),
]
class Formatter(object):
    def __init__(self, *args, **kwargs):
        pass

    def format(self, record):
        # FIXME - pretty colors if running in development.
        try:
            pieces = [formatter(record)
                      for formatter in formatters]
            lines = ' '.join(piece
                             for piece in pieces
                             if piece).split('\n')
            # Indent all but the first line.
            return '\n'.join(line if not i else '    ' + line
                             for i, line in enumerate(lines)).strip()

        except Exception:
            exc_info = sys.exc_info()
            tb = ''.join(format_exception_only(exc_info[0], exc_info[1]))
            return '[ERROR] [Bad LogRecord] {}\n{}'.format(record, tb)

# Thread-local context for Formatter.
loggy_context = threading.local()

@contextmanager
def loggy_context_manager():
    try:
        yield
    finally:
        for key in list(vars(loggy_context)):
            delattr(loggy_context, key)

if __name__ == '__main__':
    configure_logging()
    logging.getLogger('dweeb.loggy').info('loggy is here')
