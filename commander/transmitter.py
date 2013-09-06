#!/usr/bin/env python

import redis
import json
import zmq
import pprint
import argparse
import os
import urllib2
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbose mode')
args = parser.parse_args()
args.verbose = True

config = {}
if 'etcd' in os.environ:
	config['etcd'] = os.environ['etcd']
else:
	config['etcd'] = 'localhost'

print "Getting " + config['etcd']
sys.stdout.flush()

# Use etcd to pull the location of the redis server
url = 'http://' + config['etcd'] + ':4001/v1/keys/redis'
req = urllib2.Request(url)
response = urllib2.urlopen(req)
the_page = response.read()
data = json.loads(the_page)
config['redis'] = data['value']

r = redis.Redis(config['redis'])

while True:
	if args.verbose:
		print 'Waiting for something in the job_queue'
		sys.stdout.flush()
	(queue, job_id) = r.blpop('job_queue')
	if args.verbose:
		print 'Got job_id ' + str(job_id) + ' off the job_queue'
		sys.stdout.flush()
	key = 'job:' + str(job_id)
	if args.verbose:
	 	print "Getting the job from key '" + key + "'"
		sys.stdout.flush()
	job = r.get(key)
	data = json.loads(job)
	for host in data['hosts']:
		hostdata = {}
		hostdata['id'] = data['id']
		if 'command' in data:
			hostdata['command'] = data['command']
		if 'code' in data:
			hostdata['code'] = data['code']
		hostdata['host'] = host
		text = json.dumps(hostdata)
		if args.verbose:
			print 'Sending to ' + host + ': ' + text
			sys.stdout.flush()
		context = zmq.Context()
		socket = context.socket(zmq.PUSH)
		socket.connect("tcp://" + host + ":8888")
		socket.send(text)
		socket.close()
