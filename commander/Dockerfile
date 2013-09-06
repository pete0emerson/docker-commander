FROM base
MAINTAINER Pete Emerson "pete@theemersons.org"
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get remove -y vim-common
RUN apt-get install -y vim
RUN apt-get install -y python-redis
RUN apt-get install -y redis-server
RUN apt-get install -y python-zmq
RUN apt-get install -y telnet
RUN apt-get install -y curl
ADD redis.conf /etc/redis/redis.conf
ADD commander.py /root/commander.py
ADD transmitter.py /root/transmitter.py
ADD processor.py /root/processor.py
ADD receiver.py /root/receiver.py
ADD processor_list.py /root/processor_list.py
ADD inject.py /root/inject.py
