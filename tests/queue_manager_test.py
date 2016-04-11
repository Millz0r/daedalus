import daedalus.exceptions
import kombu
import mock
import unittest
from daedalus.queueing.queue_manager import _tcp_to_amqp, _is_amqp_connection_string, _is_tcp_connection_string, _create_connection_from_string, _setup_connection, _bind_queue, get_response_queue, get_queue, get_producer, set_connection, get_connection, get_channel, get_connected, close_connection

class TcpToAmqpTest(unittest.TestCase):
    def test_good_connection_string(self):
        result = _tcp_to_amqp('tcp://10.1.1.255:5000')
        self.assertEqual(result, 'amqp://10.1.1.255:5000//')

    def test_bad_connection_string(self):
        with self.assertRaisesRegexp(daedalus.exceptions.BadConnectionString, 'Not a valid TCP connection string: this is a bad string'):
            _tcp_to_amqp('this is a bad string')

    def test_no_connection_string(self):
        with self.assertRaisesRegexp(TypeError, 'expected string or buffer'):
            _tcp_to_amqp(None)

    def test_empty_connection_string(self):
        with self.assertRaisesRegexp(daedalus.exceptions.BadConnectionString, 'Not a valid TCP connection string: '):
            _tcp_to_amqp('')

    def test_username_and_password(self):
        result = _tcp_to_amqp('tcp://10.1.1.255:5000', username='foo', password='bar')
        self.assertEqual(result, 'amqp://foo:bar@10.1.1.255:5000//')

    def test_username_only(self):
        with self.assertRaisesRegexp(daedalus.exceptions.MissingFields, 'Need both username and password'):
            _tcp_to_amqp('tcp://10.1.1.1:5000', username='foo')

    def test_password_only(self):
        with self.assertRaisesRegexp(daedalus.exceptions.MissingFields, 'Need both username and password'):
            _tcp_to_amqp('tcp://10.1.1.1:5000', password='foo')

class IsAmqpConnectionStringTest(unittest.TestCase):
    def setUp(self):
        protocol = 'amqp://'
        host_name = 'localhost'
        ip_address = '10.1.1.5'
        port = '5000'
        username = 'username'
        password = 'password'
        vhost = 'vhost'
        self.full_domain = ('%s%s:%s@%s:%s/%s' % (protocol, username, password, host_name, port, vhost))
        self.full_ip = ('%s%s:%s@%s:%s/%s' % (protocol, username, password, ip_address, port, vhost))
        self.short_domain = ('%s%s:%s@%s:%s' % (protocol, username, password, host_name, port))
        self.short_ip = ('%s%s:%s@%s:%s' % (protocol, username, password, host_name, port))

    def test_amqp_full_domain(self):
        self.assertTrue(_is_amqp_connection_string(self.full_domain))

    def test_amqp_short_domain(self):
        self.assertTrue(_is_amqp_connection_string(self.short_domain))

    def test_amqp_full_ip(self):
        self.assertTrue(_is_amqp_connection_string(self.full_ip))

    def test_amqp_short_ip(self):
        self.assertTrue(_is_amqp_connection_string(self.short_ip))

    def test_bad_string(self):
        self.assertFalse(_is_amqp_connection_string('bad string'))

    def test_empty_string(self):
        self.assertFalse(_is_amqp_connection_string(''))

    def test_no_string(self):
        with self.assertRaisesRegexp(TypeError, 'expected string or buffer'):
            _is_amqp_connection_string(None)

class IsTcpConnectionStringTest(unittest.TestCase):
    def setUp(self):
        protocol = 'tcp://'
        host_name = 'localhost'
        ip_address = '10.1.1.5'
        port = '5000'
        self.full_domain = ('%s%s:%s' % (protocol, host_name, port))
        self.full_ip = ('%s%s:%s' % (protocol, ip_address, port))

    def test_tcp_full_domain(self):
        self.assertTrue(_is_tcp_connection_string(self.full_domain))

    def test_tcp_full_ip(self):
        self.assertTrue(_is_tcp_connection_string(self.full_ip))

    def test_bad_string(self):
        self.assertFalse(_is_tcp_connection_string('bad string'))

    def test_empty_string(self):
        self.assertFalse(_is_tcp_connection_string(''))

    def test_no_string(self):
        with self.assertRaisesRegexp(TypeError, 'expected string or buffer'):
            _is_tcp_connection_string(None)

class CreateConnectionFromStringTest(unittest.TestCase):
    def setUp(self):
        self.good_amqp_string = 'amqp://guest:guest@localhost:5762//'
        self.good_tcp_string = 'tcp://localhost:5762'
        self.bad_string = 'bad string'

    def test_good_amqp_string(self):
        result = _create_connection_from_string(self.good_amqp_string)
        self.assertTrue(isinstance(result, kombu.connection.Connection))

    def test_good_tcp_string(self):
        result = _create_connection_from_string(self.good_tcp_string)
        self.assertTrue(isinstance(result, kombu.connection.Connection))

    def test_bad_string(self):
        with self.assertRaisesRegexp(daedalus.exceptions.BadConnectionString, 'Not a valid connection string: bad string'):
            _create_connection_from_string(self.bad_string)

class SetupConnectionTest(unittest.TestCase):
    def setUp(self):
        self.bad_connection_string = 'bad string'
        self.good_connection_string = 'amqp://guest:guest@10.1.1.255:5000'

        self.bad_connection_object = dict()
        self.good_connection_object = kombu.Connection()

    def test_good_connection_string(self):
        result = _setup_connection(self.good_connection_string)
        self.assertIsInstance(result, kombu.connection.Connection)

    def test_bad_connection_string(self):
        with self.assertRaisesRegexp(daedalus.exceptions.BadConnectionString, 'Not a valid connection string: %s' % self.bad_connection_string):
            _setup_connection(self.bad_connection_string)

    def test_good_connection_object(self):
        result = _setup_connection(self.good_connection_object)
        self.assertEqual(result, self.good_connection_object)

    def test_bad_connection_object(self):
        with self.assertRaisesRegexp(daedalus.exceptions.BadConnectionObject, 'Not a valid connection object: %s' % str(self.bad_connection_object)):
            _setup_connection(self.bad_connection_object)

class BindQueueTest(unittest.TestCase):
    @mock.patch('kombu.Queue', auto_spec=True)
    @mock.patch('daedalus.queueing.queue_manager.__CHANNEL_POOL__', auto_spec=True)
    def test_bind(self, channel_pool_mock, queue_mock):
        channel_pool_mock.acquire.return_value = 'foo'
        _bind_queue(queue_mock)
        channel_pool_mock.acquire.assert_called_with()
        queue_mock.maybe_bind.assert_called_with('foo')
        queue_mock.declare.assert_called_with()

class GetResponseQueueTest(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.get_queue')
    def test_get_response_queue(self, get_queue_mock):
        get_response_queue()
        get_queue_mock.assert_called_with('response')

class GetQueueTest(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.__QUEUES__')
    def test_existing_queue(self, queues_mock):
        queues_mock.get.return_value = 'foo'
        self.assertEqual(get_queue('boo'), 'foo')

    @mock.patch('kombu.Queue')
    def test_new_known_queue(self, kombu_queue_mock):
        get_queue('response')
        kombu_queue_mock.assert_called_with('response')

    @mock.patch('kombu.Queue')
    def test_new_temp_queue(self, kombu_queue_mock):
        get_queue('foo', temp=True)
        kombu_queue_mock.assert_called_with('foo', durable=False, auto_delete=True)

    @mock.patch('daedalus.queueing.queue_manager.__QUEUES__')
    def test_new_unknown_queue(self, queues_mock):
        queues_mock.get.return_value = None
        with self.assertRaisesRegexp(daedalus.exceptions.MissingQueue, 'Cannot find queue .*'):
            get_queue('foo')

    @mock.patch('daedalus.queueing.queue_manager.__QUEUES__')
    @mock.patch('kombu.Queue')
    @mock.patch('daedalus.queueing.queue_manager._bind_queue')
    def test_new_queue_with_connection(self, bind_queue_mock, kombu_queue_mock, queues_mock):
        queues_mock.get.return_value = None
        kombu_queue_mock.return_value = 'foo'
        get_queue('response')
        kombu_queue_mock.assert_called_with('response')
        bind_queue_mock.assert_called_with('foo')

class GetProducerTest(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.__CONNECTED__', True)
    @mock.patch('kombu.Producer', auto_spec=True)
    @mock.patch('daedalus.queueing.queue_manager.__CHANNEL_POOL__', auto_spec=True)
    def test_get_producer(self, channel_pool_mock, producer_mock):
        channel_pool_mock.acquire.return_value = 'channel'
        get_producer()
        channel_pool_mock.acquire.assert_called_with()
        producer_mock.assert_called_with('channel', on_return=None)

    @mock.patch('daedalus.queueing.queue_manager.__CONNECTED__', True)
    @mock.patch('kombu.Producer', auto_spec=True)
    @mock.patch('daedalus.queueing.queue_manager.__CHANNEL_POOL__', auto_spec=True)
    def test_get_producer_with_on_return(self, channel_pool_mock, producer_mock):
        on_return = lambda a, b, c, d: 1+2
        channel_pool_mock.acquire.return_value = 'channel'
        get_producer(on_return=on_return)
        channel_pool_mock.acquire.assert_called_with()
        producer_mock.assert_called_with('channel', on_return=on_return)

    @mock.patch('daedalus.queueing.queue_manager.__CONNECTED__', False)
    def test_get_producer_no_connection(self):
        with self.assertRaisesRegexp(daedalus.exceptions.NotConnected, 'Must be connected to create a producer'):
            get_producer()

class SetConnectionTest(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.__CONNECTION__', True)
    def test_set_connection_with_connection(self):
        with self.assertRaisesRegexp(daedalus.exceptions.ConnectionExists, 'The connection has already been set'):
            set_connection('connection_string')

    @mock.patch('daedalus.queueing.queue_manager.__QUEUES__', {'a': 1})
    @mock.patch('daedalus.queueing.queue_manager.__CONNECTION__', None)
    @mock.patch('daedalus.queueing.queue_manager._setup_connection')
    @mock.patch('daedalus.queueing.queue_manager._bind_queue')
    def test_set_connection_no_connection(self, bind_queue_mock, setup_connection_mock):
        connection_mock = mock.MagicMock()
        setup_connection_mock.return_value = connection_mock
        set_connection('connection_string')
        connection_mock.ChannelPool.assert_called_with()
        bind_queue_mock.assert_called_with(1)

class GetConnectionTest(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.__CONNECTION__', '__CONNECTION__')
    def test_get_connection(self):
        self.assertEqual(get_connection(), '__CONNECTION__')

class GetChannelTest(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.__CHANNEL_POOL__', auto_spec=True)
    def test_get_channel(self, channel_pool_mock):
        get_channel()
        channel_pool_mock.acquire.assert_called_with()

    @mock.patch('daedalus.queueing.queue_manager.__CHANNEL_POOL__', None)
    def test_get_channel_no_connection(self):
        with self.assertRaisesRegexp(daedalus.exceptions.NotConnected, 'Must be connected to create a channel'):
            get_channel()

class GetConnectedTest(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.__CONNECTED__', '__CONNECTED__')
    def test_get_connected(self):
        self.assertEqual(get_connected(), '__CONNECTED__')

class CloseConnectionTest(unittest.TestCase):
    @mock.patch('daedalus.queueing.queue_manager.__CONNECTED__', True)
    @mock.patch('daedalus.queueing.queue_manager.__CONNECTION__', auto_spec=True)
    @mock.patch('daedalus.queueing.queue_manager.__CHANNEL_POOL__', auto_spec=True)
    @mock.patch('sys.exit')
    def test_close_connection(self, exit_mock, channel_pool_mock, connection_mock):
        close_connection()
        channel_pool_mock.force_close_all.assert_called_with()
        connection_mock.release.assert_called_with()
        exit_mock.assert_called_with(0)

    @mock.patch('daedalus.queueing.queue_manager.__CONNECTED__', False)
    @mock.patch('sys.exit')
    def test_close_connection_without_connection(self, exit_mock):
        close_connection()
        exit_mock.assert_called_with(0)
