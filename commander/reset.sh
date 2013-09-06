#!/bin/bash

# This kills all of the docker containers

echo Killing all running containers ...
for i in `sudo docker ps | grep -v ID | awk '{print $1}'`; do
	sudo docker kill $i
done

echo Clearing out etcd
curl -L http://127.0.0.1:4001/v1/keys/redis -X DELETE
echo
curl -L http://127.0.0.1:4001/v1/keys/processors -X DELETE
echo
curl -L http://127.0.0.1:4001/v1/keys/receivers -X DELETE
echo
