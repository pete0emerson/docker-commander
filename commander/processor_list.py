#!/usr/bin/env python

#!/usr/bin/env python

import json
import os
import urllib2

config = {}
if 'etcd' in os.environ:
	config['etcd'] = os.environ['etcd']
else:
	config['etcd'] = 'localhost'

# Use etcd to pull the location of the receivers
url = 'http://' + config['etcd'] + ':4001/v1/keys/processors'
req = urllib2.Request(url)
response = urllib2.urlopen(req)
the_page = response.read()
data = json.loads(the_page)
l = data['value'].split(',')
print '--host=' + ' --host='.join(l)
