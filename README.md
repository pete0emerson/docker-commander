Installation dependencies

* [Virtualbox][virtualbox] 4.0 or greater.
* [Vagrant][vagrant] 1.2.3 or greater.

Clone the repository

```
~ $ git clone https://github.com/pete0emerson/docker-commander/
~ $ cd docker-commander
```

Bring the CoreOS VM up. It will download the image if you don't have it already.

```
docker-commander $ vagrant up
```

The setup.py script will copy necessary code to the CoreOS VM. If --disable-reboot is thrown, CoreOS won't auto-update and reboot itself.
--reconfigure-etcd is necessary to open etcd up to the Docker containers, but in the next release of CoreOS this will be the default.

```
docker-commander $ ./setup.py --commander --disable-reboot --reconfigure-etcd
```

Get into the CoreOS VM.


```
docker-commander $ vagrant ssh
core@localhost ~ $ cd commander
```

Build the docker image from scratch (below) or skip and the image pete/base will be downloaded from https://index.docker.io.

```
sudo docker build -t USERNAME/NAME .
```

Bring up the redis server, one or more receivers, one or more transmitters, and one or more processors.
If you built your own Docker image, the launch.py commands below will need --image USERNAME/NAME added to them.

```
core@localhost ~/commander $ ./launch.py --type=redis
core@localhost ~/commander $ ./launch.py --type=receiver     # Run more than one if you want
core@localhost ~/commander $ ./launch.py --type=transmitter  # Run more than one if you want
core@localhost ~/commander $ ./launch.py --type=processor    # Run a bunch of these! (I've run @50 of them)
```

Fire up a new container and run a shell.

```
core@localhost ~/commander $ ./launch.py --type=bash
/usr/bin/sudo docker run -i -t -e etcd=172.17.42.1 pete/base /bin/bash
```

processor_list.py makes it easy to cut and paste the host list, especially when you've got lots of processors running.

```
root@8765b127b0e2:/# /root/processor_list.py
--host=172.17.0.62 --host=172.17.0.64 --host=172.17.0.65
```

Run commander.py with the host list from above.

```
root@8765b127b0e2:/# /root/commander.py --host=172.17.0.62 --host=172.17.0.64 --host=172.17.0.65 --command=hostname
172.17.0.62 => ca08c89b579d
172.17.0.64 => ca8da7d144cc
172.17.0.65 => 5a50c396303d
```
