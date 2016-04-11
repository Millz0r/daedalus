''' Prepare testcases for nosetests '''

import mock
import unittest

from ._mock_session import MockSession

from daedalus.common.db import DBSession


class AppTest(unittest.TestCase):
    pass


class MockDatabaseTest(AppTest):
    """Run tests against a mock query system."""

    def setUp(self):
        super(MockDatabaseTest, self).setUp()
        DBSession.SESSIONMAKER = MockSession()

    def tearDown(self):
        super(MockDatabaseTest, self).tearDown()
