import os
import time

from fabric.api import env, local, run

SERVICES = {
    'rabbitmq': {
        'unit': './share/data/units/deis/rabbitmq@.service'
    },
    'postgres': {
        'unit': './share/data/units/vagrant/postgres@.service',
        'username': 'daedalus',
        'password': 'godaedalusgo',
        'schema': 'daedalus'
    },
    'daedalus': {
        'unit': './share/data/units/vagrant/daedalus@.service'
    }
}
 
def vagrant():
    '''Setup vagrant connection.'''
    # change from the default user to 'vagrant'
    env.user = 'core'

    # local env variable `SSH_CONFIG` should point to a file that contains an entry with the output of `vagrant ssh-config`
    if os.environ.get("SSH_CONFIG"):
        env.use_ssh_config = True
        env.hosts = ["daedalus-01"]
        local('vagrant rsync')
    else:
        # connect to the port-forwarded ssh
        env.hosts = ['127.0.0.1:2222']
        # use vagrant ssh key
        result = local('vagrant ssh-config | grep IdentityFile', capture=True)
        env.key_filename = result.split()[1]


def update_service(unit_name):
    '''Destroys the template service files and loads the new ones into fleet.'''
    run('fleetctl destroy {service_unit}'.format(service_unit=SERVICES[unit_name]['unit']))
    run('fleetctl submit {service_unit}'.format(service_unit=SERVICES[unit_name]['unit']))

def start_service(unit_name, environment='development'):
    '''Starts the service.'''
    service = SERVICES[unit_name]['unit'].replace(".", "daedalus-{environment}.".format(environment=environment))
    run('fleetctl stop {service}'.format(service=service))
    run('fleetctl destroy {service}'.format(service=service))
    time.sleep(2)
    run('fleetctl start {service}'.format(service=service))

def create_env_file():
    '''Creates environment file'''
    # required to connect to etcd
    run("echo ETCD_ENDPOINT=$(ifconfig docker0 | awk '/inet / { print $2 }'):4001 > /tmp/env.file")
    # required to connect to postgres
    run('echo POSTGRES_URL=postgres://{username}:{password}@{host}:5432/{schema} >> /tmp/env.file'.format(
        username=SERVICES['postgres']['username'],
        password=SERVICES['postgres']['password'],
        host="$(ifconfig docker0 | awk '/inet / { print $2 }')",
        schema=SERVICES['postgres']['schema'],
    ))

def prefetch_image():
    '''Prefetches the docker image so services can start without having to fetch.'''
    run('docker pull dockerfile/rabbitmq')
    run('docker pull jamesbrink/postgresql')
    run('docker build -t daedalus-dev /home/core/share/')

def deploy(unit_name="daedalus", environment='development'):
    '''Recreates the service and (re)starts it.'''
    update_service(unit_name)
    start_service(unit_name, environment)

def setup(environment='development'):
    '''Setup all the requirements for running the code. Should be run only once after the first `vagrant up`.'''
    prefetch_image()
    deploy("rabbitmq", environment)
    deploy("postgres", environment)
    create_env_file()
    deploy("daedalus", environment)

def logs(service="daedalus", environment='development'):
    '''Shows the logs of the specified service.'''
    run('fleetctl journal -f {service}@daedalus-{environment}.service'.format(service=service, environment=environment))

def shell(environment="development"):
    '''Opens a shell inside the deocker container runnign the daedalus code.'''
    run("docker exec -it daedalus-{environment} /bin/bash".format(environment=environment))

def tests(environment="development"):
    '''Runs the nose tests for daedalus code.'''
    run("docker exec -it daedalus-{environment} python setup.py nosetests".format(environment=environment))

def lint(environment="development"):
    '''Runs pylint for daedalus code.'''
    run("docker exec -it daedalus-{environment} python setup.py lint".format(environment=environment))
