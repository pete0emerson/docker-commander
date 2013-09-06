#!/usr/bin/env python

import zmq
import json
import subprocess
from multiprocessing import Process
from time import sleep
import os
from tempfile import mkstemp
import argparse
import urllib2
import sys
import random

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbose mode')
args = parser.parse_args()

config = {}
if 'etcd' in os.environ:
	config['etcd'] = os.environ['etcd']
else:
	config['etcd'] = 'localhost'

# Use etcd to pull the location of the receivers
url = 'http://' + config['etcd'] + ':4001/v1/keys/receivers'
req = urllib2.Request(url)
response = urllib2.urlopen(req)
the_page = response.read()
data = json.loads(the_page)
receivers = data['value'].split(',')

def getJob(socket):
	if args.verbose:
		print "Waiting for a job to process"
		sys.stdout.flush()
	message = socket.recv()
	if args.verbose:
		print 'Got a job: ' + message
		sys.stdout.flush()
	return json.loads(message)

def processCommand(data):
	if 'code' in data:
		(fd, file) = mkstemp(prefix='code_', dir='/tmp')
		f = os.fdopen(fd, "w")
		f.write(data['code'])
		f.close()
		os.chmod(file, 0755)
		data['command'] = file
	proc = subprocess.Popen(data['command'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	stdout_value, stderr_value = proc.communicate('')
	data['exit_code'] = proc.returncode
	data['results'] = str(stdout_value)
	if 'code' in data:
		os.remove(file)
	text = json.dumps(data)
	randint = random.randint(0, len(receivers) - 1)
	receiver = receivers[randint]
	if args.verbose:
		print 'Sending to ' + receiver + ': ' + text
		sys.stdout.flush()
	context = zmq.Context()
	rep = context.socket(zmq.PUSH)
	rep.connect('tcp://' + receiver + ':9999')
	rep.send(text)
	rep.close()

def cleanupProcesses(procs):
	for p in procs:
		if not p.is_alive():
			p.join()
			procs.remove(p)
	return procs

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:8888")
procs = []
while True:
	data = getJob(socket)
	p = Process(target=processCommand, args=(data,))
	p.start()
	procs.append(p)
	procs = cleanupProcesses(procs)
