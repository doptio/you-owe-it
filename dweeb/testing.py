from __future__ import unicode_literals, division

from contextlib import contextmanager
from mock import patch
import os
import sys

__all__ = ['assert_raises', 'assert_eq', 'setup_hooks']

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

    def setup_function():
        module.app.db.create_all()
        module.client = module.app.test_client()
        local_setup()

    def teardown_function():
        local_teardown()
        del module.client
        module.app.db.drop_all()

    for name, value in module.__dict__.items():
        if name.startswith('test_') and callable(value):
            value.setup = setup_function
            value.teardown = teardown_function


def setup_module(m):
    setup_hooks(m.__name__)
