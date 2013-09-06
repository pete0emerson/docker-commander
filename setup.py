#!/usr/bin/env python

import glob
import subprocess
import sys
import argparse

parser = argparse.ArgumentParser(description='Copy files to the CoreOS VM')
parser.add_argument('--debug', default=False, action='store_true')
parser.add_argument('--backup', default=False, action='store_true')
parser.add_argument('--commander', default=False, action='store_true')
parser.add_argument('--reconfigure-etcd', default=False, action='store_true')
parser.add_argument('--disable-reboot', default=False, action='store_true')
args = parser.parse_args()

try:
	ssh_config = subprocess.check_output(["vagrant", "ssh-config"])
except:
	print "\n\nSomething went drastically wrong. Are you in your vagrant directory?\n"
	sys.exit(1)

config = {}
for l in ssh_config.split("\n"):
	l = l.strip()
	if ' ' in l:
		key, value = l.split()
		config[key] = value

okay = True
for k in ['Host', 'HostName', 'User', 'Port', 'IdentityFile']:
	if k not in config:
		print k + ' is not in the output of ssh-config'
		print "\n", ssh_config
		okay = False

if not okay:
	sys.exit(1)

if args.backup:
	ssh_command = ['scp', '-o', 'LogLevel=quiet', '-r', '-i', config['IdentityFile'], '-P', config['Port'], config['User'] + '@' + config['HostName'] + ':commander', '.']
	print ' '.join(ssh_command)
	if not args.debug:
		result = subprocess.call(ssh_command)
elif args.commander:
	ssh_command = ['scp', '-o', 'LogLevel=quiet', '-r', '-i', config['IdentityFile'], '-P', config['Port'], 'commander', config['User'] + '@' + config['HostName'] + ':']
	print ' '.join(ssh_command)
	if not args.debug:
		result = subprocess.call(ssh_command)

if args.reconfigure_etcd:
	ssh_command = ['scp', '-o', 'LogLevel=quiet', '-i', config['IdentityFile'], '-P', config['Port'], 'coreos/etcd-local.service', config['User'] + '@' + config['HostName'] + ':']
	print ' '.join(ssh_command)
	if not args.debug:
		result = subprocess.call(ssh_command)

	ssh_command = ['ssh', '-o', 'LogLevel=quiet', '-i', config['IdentityFile'], '-p', config['Port'], config['User'] + '@' + config['HostName'], 'sudo', 'cp', './etcd-local.service', '/media/state/units']
	print ' '.join(ssh_command)
	if not args.debug:
		result = subprocess.call(ssh_command)

	ssh_command = ['ssh', '-o', 'LogLevel=quiet', '-i', config['IdentityFile'], '-p', config['Port'], config['User'] + '@' + config['HostName'], 'sudo', 'systemctl', 'restart', 'local-enable.service']
	print ' '.join(ssh_command)
	if not args.debug:
		result = subprocess.call(ssh_command)

if args.disable_reboot:
	ssh_command = ['ssh', '-o', 'LogLevel=quiet', '-i', config['IdentityFile'], '-p', config['Port'], config['User'] + '@' + config['HostName'], 'sudo', 'systemctl', 'stop', 'update-engine-reboot-manager.service']
	print ' '.join(ssh_command)
	if not args.debug:
		result = subprocess.call(ssh_command)
