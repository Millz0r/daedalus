#Daedalus
Daedalus is a real-time property analytics engine. This is an abandonded project I used to work on displayed as a showcase.

##Main files and directories

* **daedalus** - directory for the files that will be put into the Docker container and deployed remotely as part of the Daedalus product.
* **setup.py** - used to set up configure a development system.
* **data** - Excel and text sample data used in tests.
* **tests** - automated tests.

##Setup: Linux / OS X

0. Install Python
    * **Python 2.7** - https://www.python.org/download/releases/2.7/

1. Install Dependencies
    * **Setuptools** - https://pypi.python.org/pypi/setuptools
    * **Pip** - http://pip.readthedocs.org/en/latest/installing.html
    * **RabbitMQ** - http://www.rabbitmq.com/
    * **Numpy** - http://www.numpy.org/
    * **Scipy** - http://sourceforge.net/projects/scipy/
    * **Pandas** - http://pandas.pydata.org/
    * **LibMagic** - http://sourceforge.net/projects/libmagic/

    You might encounter an error installing Scipy. This is due to dev dependencies missing. To fix that, manually download those:
    `sudo apt-get install gfortran libopenblas-dev liblapack-dev libffi-dev`

2. Clone the Repository - https://github.com/Millz0r/daedalus

3. Run PIP for Development
This will download all dependencies for the application and install them as well as symlink the daedalus project to the libraries folder.
    * In the command line, navigate to the local repository
    * Type: `pip install -r requirements.txt`

OR OPTIONAL: Setup `virtualenv`

##Setup: Windows / Linux / OS X

* **Vagrant** - https://www.vagrantup.com/
    * _(Windows Only)_ **Vagrant Windows NFS Disk Plugin** - `vagrant plugin install vagrant-winnfsd`
* **VirtualBox** - https://www.virtualbox.org/wiki/Downloads
    * **VirtualBox Extension Pack** - https://www.virtualbox.org/wiki/Downloads

##Setup: Vagrant
A vagrant file is shipped with Daedalus to allow for cluster configurations and testing on a local development machine.
Before doing anything else make sure you have `fabric` installed locally as it will be used to run commands on the VM, like starting the services or running tests, and `rsync` is on your path to sync folders with the VM.


**Windows Only** users should make sure to have `rsync` available, like install MinGW http://sourceforge.net/projects/mingw/files/MinGW/ or http://cygwin.com/install.html. We need it for the shared folders.

**Windows Only** run `vagrant ssh-config` and paste its output into a file. Add that file to the environment as `SSH_CONFIG`, fabric will use it to connect to the vagrant VM.

To start the vagrant machine run the following commands:

```sh
vagrant up
vagrant ssh
```

You should now be in your virtual machine. By default there's only one machine started. We may change that as we get more services running. Port 80 on the virtual machine is exposed on the host machine's port 8081.

To exit just type `exit`.

###Fabric

To start the services we use `fabric` on the host that will execute commands on the guest vagrant for starting the services and running tests.

Fabric defines the `vagrant` details based on the default forwarded port `2222`. The port might change if you have multiple vagrant machines running, so make sure this one is on `2222`.

All the fabric commands call `vagrant` which ensures it is using the correct ssh key and calls `vagrant rsync` to make sure the VM is using the latest code. Not passing vagrant as the second argument will cause this output:

`No hosts found. Please specify (single) host string for connection: `

####Setup
After the VM was created the first time, you should run 

`fab vagrant setup`

This will:

* prefetch the docker images 
* initialize and start `rabbitmq` service using `data/units/deis/rabbitmq@.service` (same as `fab vagrant deploy:rabbitmq`)
* creates env file with `etcd` ip for daedalus to fetch `rabbitmq` connection details (same as `fab vagrant create_env_file`)
* initialize and start `daedalus` service `data/units/vagrant/daedalus@.service` (same as `fab vagrant deploy`)

The first time you run it give it a few minutes.

To verify the frontend is working run from the host (your local):

`curl --user yambo:groot? localhost:8081/ping`

If it doesnt work, ssh in the vagrant machine and check the units are running. See [CoreOS](https://coreos.com) for more info about `fleet` and other CoreOS utilities.

####Provision
To provision your vagrant machine with latest code and make sure it runs it, call

`fab vagrant deploy`

This will `rsync` the folders and it will (re)start the `daedalus` service which recreates the docker container to run the latest code. The local deploy uses the `honcho` app to start one instance of each process defined in `Procfile`.

####Adding a new process
When you need to start a new process on the docker container, append its command to `Procfile` and call `fab vagrant deploy`.

####Testing Development Code
To run the tests call:

`fab vagrant tests`

This will sync the files and execute `python setup.py nosetests` inside the docker container that runs the daedalus service.

####PyLint
You can call `pylint` with

`fab vagrant lint`

####Logs
You can access the logs of the running processes by calling:

`fab vagrant logs`

####Shell
If you need access to a shell inside the docker container, run:

`fab vagrant shell`

##Deployment on Deis
Current deploy strategy uses the `Dockerfile` (to fetch the python base image and install dependencies) and `Procfile` to be able to control what services should start.

By default deis will start the `cmd` process and Docker has no problem running them on the same container too but you will have to scale them manually.

If you want to run the processes on individual apps, make sure to run `deis scale cmd=0`.

###Prerequisites
Before creating any environment, make sure rabbitmq is running using the `data/units/deis/rabbitmq@.service` service file (which you should manually create on deis server if its not already there).

Naming the service `daedalus-development` is very important as that relates to the `daedalus-development` release type set as environment variable and its used as the `etcd` key for storing connection details in the key `/services/queue/daedalus-{environment}`.

```
fleetctl submit rabbitmq@.service
fleetctl start rabbitmq@daedalus-development.service
```

The service will also set the credentials to connect to this instance of rabbitmq in the etcd structure.

###Sample deploy
Sample deploy for `daedalus-development`:

```
git checkout development
deis create daedalus-development
deis config:set ETCD_ENDPOINT=172.17.42.1:4001 ENVIRONMENT=daedalus-development
deis perms:create codeship
git push deis development:master

deis scale scheduler=1
deis scale transform=1
deis scale valuate=1
```

Running `deis config:set ENVIRONMENT=development` ensures it will connect to the appropriate rabbitmq service.


###Adding a new process
When you create a new process that needs to start, append its command to `Procfile`.

`newprocess: newprocess.service`

When the code has been merged and deployed make sure to start the process on deis too.

`deis scale newprocess=1`

####TO DO
Find a way to scale the processes on deploy?
