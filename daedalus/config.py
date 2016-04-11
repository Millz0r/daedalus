# pylint: disable=no-member,bare-except,invalid-name,line-too-long
'''Configuration settings for the daedalus platform.'''

import json
import os
from daedalus.common import config_manager

ENVIRONMENT = os.environ.get('ENVIRONMENT')

etcd_rabbitmq_key = '/services/queue/{environment}'.format(environment=ENVIRONMENT)
rabbitmq_config = config_manager.get(etcd_rabbitmq_key)
if rabbitmq_config is not None:
    RABBITMQ_PORT = 'amqp://guest:guest@{host}:{port}'.format(**json.loads(rabbitmq_config))
else:
    RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', 'amqp://guest:guest@localhost:5672')

POSTGRES_URL = os.environ.get('POSTGRES_URL', 'postgres://localhost:5432')

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

ALLOWED_DOMAINS = ['localhost', '127.0.0.1']
