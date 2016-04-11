#!/bin/bash

if [ ! -f /tmp/provisioned ]; then
    sed -e "s,discovery: https://discovery.etcd.io/.*,discovery: $(curl -s -w '\n' https://discovery.etcd.io/new)," /home/core/share/user-data.example > /var/lib/coreos-vagrant/vagrantfile-user-data
    systemctl start fleet
	touch /tmp/provisioned
fi
