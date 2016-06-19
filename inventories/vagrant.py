#!/usr/bin/env python

import os
import json
import subprocess
import sys
import time
import shutil

cmd = "vagrant ssh-config"
cache_file = ".vagrant-ansible-inventory.cache"
cache_expiration = 180
default_json_output = json.dumps({"_meta": {"hostvars" : {}}})

# TODO: maybe check for existence of vagrand installation - not critical

# Find Vagantfile dir, recursive find parent dirs
vagrantdir = ""
actual_dir = os.path.dirname(os.path.realpath(__file__))
while True:
	parent_dir = os.path.dirname(actual_dir)

	vagrantfile = os.path.join(parent_dir, "Vagrantfile")
	if os.path.isfile(vagrantfile):
		vagrantdir = parent_dir
		break
	if parent_dir == actual_dir:
		sys.stderr.write( "Vagrantfile not found in parent directories.\n")
		sys.exit(0) 
	actual_dir = parent_dir

# Load inventory from cache if valid
cache_file_path = os.path.join(vagrantdir, cache_file)
if os.path.isfile(cache_file_path) and (time.time() - os.path.getmtime(cache_file_path)) < cache_expiration:
	with open(cache_file_path, "r") as f:
		shutil.copyfileobj(f, sys.stdout)
	sys.exit(0)

# Generate inventor
try:
    pipes = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
except:
    sys.stderr.write( "Vagrant probably no running. Unexpected error: " + str(sys.exc_info()) + "\n" )
    sys.stdout.write( default_json_output )
    sys.exit(0)
std_out, std_err = pipes.communicate()                                                                                             
   
# Vagrant is not ready for ssh
if pipes.returncode != 0:
    sys.stderr.write( "Failed to execute command '%s', return code: %d\n" % (cmd, pipes.returncode) )
    sys.stdout.write( default_json_output )
    sys.exit(0)

hostvars = {}
groups = {}

# Parse vagrant ssh config
vagrant_ssh_config = std_out.split("Host ")[1::]
for host_ssh_config in vagrant_ssh_config:
    # Parse
    lines = host_ssh_config.split('\n')
    server_name = lines[0]

    host_config = {}
    for definition in lines[1::]:
        parts = definition.strip().split(" ", 1)
        if len(parts) == 2:
            host_config[parts[0]] = parts[1]
   
    # Store host
    hostvars[server_name] = {
      "ansible_user": host_config['User'],
      "ansible_host": "vagrant", #host_config['HostName'],
      "ansible_port": host_config['Port'],
      "ansible_ssh_private_key_file": host_config['IdentityFile'].strip("\"")
    }
   
    # Add host to group
    group_name = server_name.rsplit('-', 1)[0]
    if not group_name in groups:
        groups[group_name] = []
    groups[group_name].append(server_name)

# Print inventory
inventory = {
	"_meta": {
	    "hostvars" : hostvars
	}
}

for group, group_hosts in groups.iteritems():
    inventory[group] = []
    for group_host in group_hosts:
    	inventory[group].append(group_host)

json_inventory = json.dumps(inventory)
with open(cache_file_path, 'w') as f:
    f.write(json_inventory)
sys.stdout.write(json_inventory)
