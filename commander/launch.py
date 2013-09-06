#!/usr/bin/env python

import argparse
import subprocess
import socket
import urllib2
import sys
import json
from time import sleep
import os

parser = argparse.ArgumentParser(description='Launch the commander demo containers')
parser.add_argument('--image', default='pete/base')
parser.add_argument('--type', required=True)
args = parser.parse_args()

ip_address = subprocess.check_output("/bin/ifconfig").split("\n")[1].split()[1]

if args.type == 'redis':
	command = "sudo docker run -d " + args.image + " /usr/bin/redis-server"
	print command
	command_arr = command.split(' ')
	container_id = subprocess.check_output(command_arr).strip()
	command = "sudo docker inspect " + container_id
	print command
	command_arr = command.split(' ')
	inspection = subprocess.check_output(command_arr)
	data = json.loads(inspection)
	redis_ip = data[0]['NetworkSettings']['IPAddress']
	url = 'http://127.0.0.1:4001/v1/keys/redis'
	payload = 'value=' + redis_ip
	req = urllib2.Request(url, payload)
	response = urllib2.urlopen(req)
	the_page = response.read()
	print url, payload
	print the_page
elif args.type == 'transmitter':
	command = "sudo docker run -d -e etcd=" + ip_address + " " + args.image + " /root/transmitter.py --verbose"
	print command
	command_arr = command.split(' ')
	container_id = subprocess.check_output(command_arr).strip()
	print container_id
elif args.type == 'receiver':
	command = "sudo docker run -d -e etcd=" + ip_address + " " + args.image + " /root/receiver.py --verbose"
	print command
	command_arr = command.split(' ')
	container_id = subprocess.check_output(command_arr).strip()
	print container_id
	command = "sudo docker inspect " + container_id
	print command
	command_arr = command.split(' ')
	inspection = subprocess.check_output(command_arr)
	data = json.loads(inspection)
	receiver_ip = data[0]['NetworkSettings']['IPAddress']
	url = 'http://127.0.0.1:4001/v1/keys/receivers'
	req = urllib2.Request(url)
	try:
		response = urllib2.urlopen(req)
		the_page = response.read()
		print the_page
		d = json.loads(the_page)
		receiver_ips = d['value'].split(',')
		if receiver_ip not in receiver_ips:
			receiver_ips.append(receiver_ip)
	except:
		receiver_ips = [receiver_ip]
	url = 'http://127.0.0.1:4001/v1/keys/receivers'
	payload = 'value=' + ','.join(receiver_ips)
	req = urllib2.Request(url, payload)
	response = urllib2.urlopen(req)
	the_page = response.read()
	print url, payload
	print the_page
elif args.type == 'processor':
	command = "sudo docker run -d -e etcd=" + ip_address + " " + args.image + " /root/processor.py --verbose"
	print command
	command_arr = command.split(' ')
	container_id = subprocess.check_output(command_arr).strip()
	print container_id
	command = "sudo docker inspect " + container_id
	print command
	command_arr = command.split(' ')
	inspection = subprocess.check_output(command_arr)
	data = json.loads(inspection)
	processor_ip = data[0]['NetworkSettings']['IPAddress']
	url = 'http://127.0.0.1:4001/v1/keys/processors'
	req = urllib2.Request(url)
	try:
		response = urllib2.urlopen(req)
		the_page = response.read()
		print the_page
		d = json.loads(the_page)
		processor_ips = d['value'].split(',')
		if processor_ip not in processor_ips:
			processor_ips.append(processor_ip)
	except:
		processor_ips = [processor_ip]
	url = 'http://127.0.0.1:4001/v1/keys/processors'
	payload = 'value=' + ','.join(processor_ips)
	req = urllib2.Request(url, payload)
	response = urllib2.urlopen(req)
	the_page = response.read()
	print url, payload
	print the_page
elif args.type == 'bash':
	command = "/usr/bin/sudo docker run -i -t -e etcd=" + ip_address + " " + args.image + " /bin/bash"
	print command
	os.execl('/usr/bin/sudo', '/usr/bin/sudo', 'docker', 'run', '-i', '-t', '-e', 'etcd=' + ip_address, args.image, '/bin/bash')
