# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'yaml'
require "fileutils"

configuration = YAML::load(File.read("#{File.dirname(__FILE__)}/group_vars/all.yml"))

Vagrant.configure(2) do |config|

	config.vm.synced_folder '.', '/vagrant', disabled: true

	configuration['servers'].each_with_index do |(name, server_config),server_index|
		config.vm.define name do |node|
			node.vm.box = server_config['image']
			node.vm.hostname = name
			node.vm.network "private_network", type: "dhcp"

			node.vm.provider "virtualbox" do |v|
				v.memory = server_config['memory']
				v.cpus = server_config['cpus']
				v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
				v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
			end

			server_config['opened_ports'].each do |port_def|
				if port_def['port'] == 22
					node.vm.network "forwarded_port", guest: 22, host: 10000 + (server_index * 1000) + 22, id: "ssh", protocol: "tcp", auto_correct: true
				else
					node.vm.network "forwarded_port", guest: port_def['port'], host: 10000 + (server_index * 1000) + port_def['port'], protocol: port_def['protocol'], auto_correct: true
				end
			end
		end
	end
end