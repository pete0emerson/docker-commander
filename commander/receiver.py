#!/usr/bin/env python

import redis
import zmq
import json
import argparse
import os
import urllib2
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbose mode')
args = parser.parse_args()

config = {}
if 'etcd' in os.environ:
	config['etcd'] = os.environ['etcd']
else:
	config['etcd'] = 'localhost'

# Use etcd to pull the location of the redis server
url = 'http://' + config['etcd'] + ':4001/v1/keys/redis'
req = urllib2.Request(url)
response = urllib2.urlopen(req)
the_page = response.read()
data = json.loads(the_page)
config['redis'] = data['value']


r = redis.Redis(config['redis'])

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:9999")
while True:
	if args.verbose:
		print "Waiting for a job result"
		sys.stdout.flush()
	message = socket.recv()
	if args.verbose:
		print 'Got job result: ' + message
		sys.stdout.flush()
	data = json.loads(message)
	job_id = data['id']
	host = data['host']
	key = 'job_result:' + str(job_id) + ':' + host
	if args.verbose:
		print 'Storing key ' + key + ' ==> ' + message
		sys.stdout.flush()
	r.set(key, message)
	key = 'job_done:' + str(job_id)
	r.rpush(key, host)
