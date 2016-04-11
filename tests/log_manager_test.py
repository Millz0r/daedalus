import daedalus.common.log_manager
import logging
import mock
import unittest

class LogManagerTest(unittest.TestCase):

    def test_get_log_level_default_level(self):
        self.assertEqual(daedalus.common.log_manager._get_log_level(), logging.INFO)

    @mock.patch('daedalus.config.LOG_LEVEL', 'Foo')
    def test_get_log_level_bad_level(self):
        self.assertEqual(daedalus.common.log_manager._get_log_level(), logging.INFO)

    @mock.patch('daedalus.config.LOG_LEVEL', 'DEBUG')
    def test_get_log_level_good_level(self):
        self.assertEqual(daedalus.common.log_manager._get_log_level(), logging.DEBUG)

    @mock.patch('logging.debug')
    def test_debug(self, debug_mock):
        daedalus.common.log_manager.debug('foo')
        debug_mock.assert_called_with('foo')

    @mock.patch('logging.info')
    def test_debug(self, info_mock):
        daedalus.common.log_manager.info('foo')
        info_mock.assert_called_with('foo')

    @mock.patch('logging.warn')
    def test_debug(self, warn_mock):
        daedalus.common.log_manager.warn('foo')
        warn_mock.assert_called_with('foo')

    @mock.patch('logging.error')
    def test_debug(self, error_mock):
        daedalus.common.log_manager.error('foo')
        error_mock.assert_called_with('foo')

    @mock.patch('logging.critical')
    def test_debug(self, critical_mock):
        daedalus.common.log_manager.critical('foo')
        critical_mock.assert_called_with('foo')
