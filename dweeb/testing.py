from __future__ import unicode_literals, division

from contextlib import contextmanager
from mock import patch
import os
from resolver import resolve
from sqlalchemy import create_engine
import sys

from dweeb import database

__all__ = ['assert_raises', 'assert_eq', 'create_database', 'setup_hooks']

@contextmanager
def assert_raises(expected_exception):
    '''Context manager for use in tests, where an exception is expected.

    Use like this::

        with assert_raises(Exception):
            raise Exception('I should fail')

    If an instance of :param:`expected_exception` is not raised this will
    raise AssertionError.'''

    try:
        yield
    except expected_exception:
        pass
    else:
        raise AssertionError('%s was not raised'
                             % expected_exception.__name__)

def assert_eq(actual, expected):
    'Assert that two values compare equal.'
    assert actual == expected, '%r not == expected %r' % (actual, expected)

def setup_hooks(module_name):
    '''Setup per-test setup/teardown hooks for all tests in module.

    This is equivalent to decorating each test-function in the module with
    ``@with_setup(setup_function, teardown_function)``.'''

    module = sys.modules[module_name]
    local_setup = getattr(module, 'setup_function', lambda: None)
    local_teardown = getattr(module, 'teardown_function', lambda: None)

    Base = resolve(os.environ.get('ORM_BASE'))
    orig_session_factory = database.session_factory

    def setup_function():
        engine = create_engine('sqlite://')
        Base.metadata.create_all(bind=engine)

        module.session = orig_session_factory(bind=engine)
        database.session_factory = MockSession(module.session)

        local_setup()

    def teardown_function():
        local_teardown()

        orig_session_factory.remove()
        database.session_factory = orig_session_factory
        module.session = None

    for name, value in module.__dict__.items():
        if name.startswith('test_') and callable(value):
            value.setup = setup_function
            value.teardown = teardown_function

class MockSession(object):
    def __init__(self, session):
        self.session = session

    def __call__(self):
        return self.session

    def remove(self):
        pass

def setup_module(m):
    setup_hooks(m.__name__)


class MockRedis(dict):
    def set(self, key, value):
        self[key] = value

    def expire(self, key, value):
        pass

@contextmanager
def mock_cache():
    with patch('dweeb.cache.redisses', MockRedis()) as mock:
        yield mock
