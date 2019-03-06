# Poster [![Build Status](https://travis-ci.org/gis4dis/poster.svg?branch=master)](https://travis-ci.org/gis4dis/poster)

Application for geo-spatial data collection and processing. 

## Requirements for production

* Python 3.2+

Note: To use geo-features for django (GDAL, GEOS, PROJ), you need to have set env variable:
BUILD_WITH_GEO_LIBRARIES=1
see:
https://help.heroku.com/ONEQG0L6/how-do-i-enable-geo-libraries-e-g-geodjango-for-use-with-python

## Requirements for local development
* docker (https://www.docker.com/community-edition#/download)
  * Linux post-install: [enable Docker for non-root user](https://docs.docker.com/install/linux/linux-postinstall/)
* docker-compose (https://docs.docker.com/compose/install/)

both installed on localhost.

## How to run local dev environment

- run
```bash
git clone git@github.com:gis4dis/poster.git
cd poster

# copy exapmle.env as .env - it should have reasonable defaults.
cp example.env .env
```

- clone any version of your choice of Luminol:

```bash
cd src/
git clone git@github.com:gis4dis/luminol.git
cd -
```

- If you have PostgreSQL (or something else) running at local port 5432, stop it.

- run
```bash 
# Run the whole cluster on localhost { Django + Celery + Redis + Postgis + (Mongo) }.
# The first run will also runs `docker-compose build` automatically, which builds the "web" docker container and downloads other containers.
docker-compose up

# Make django migrations (creates DB structures).
./dcmanage.sh migrate
# Windows: docker-compose run --rm poster-web python manage.py migrate

# Create Django superuser
./dcmanage.sh createsuperuser
# Windows: docker-compose run --rm poster-web python manage.py createsuperuser
```
- Login with superuser at http://localhost:8000/admin

- You can also import and aggregate some data
```
# import some meteorological data
./dcmanage.sh ala_import

# aggregate it
./dcmanage.sh aggregate_observations
```
You can check imported data at http://localhost:8000/admin/ala/observation/. Notice that aggregation is computed in the background. You can check the state at http://localhost:5555/tasks.


### Other basic commands

#### `docker-compose build`
(Re)builds the "web" docker container.

This will (re)build the web docker image with new 
 *requirement.txt* file

For more information see *Dockerfile*.

#### `docker-compose rm -v`
This command removes created temporary volumes that were
 attached to docker containers.
 
#### `docker-compose down -v`
This command removes created named volumes, e.g. the database.
 
When the docker containers are not properly shut, 
 the attached volume(s) can in some cases stay
 detached but created and running `docker-compose up` will
 end with error, complaining about "same volume names".

### Advanced commands

#### `docker-compose up | tee docker.log`

Taken from `man tee` page:

|*tee - read from standard input and write to standard output and files*

This command will send output (logs) of all docker containers to:
* terminal
* file `docker.log`

You can use this log file to further examine and filter logs with your
 favorite tool. (grep, less, ...)
 The logfile will get erased on every new run (feature).
 
#### `less -R docker.log` + `&search-term⏎`

This will open *docker.log* file in less (-R flag preserves 
 the terminal colors). Then you can you in-build filter function
 to obtain only the logs you are interested in.

#### `sudo docker-compose logs --tail 20 poster_celery_worker`
This will display last 20 log messages from `poster_celery_worker` service.
 You can find the service names in *docker-compose.yml* file as well as in
 the log prepended on each line. 
 
If you omit the `--tail #` flag it will display **all logs** 
 from **all previous runs**. Use it with caution.

#### Export DB (dump)
Replace <NAME> for proper variable, this will also prompt for DB password
```
pg_dump -h <HOST> -p <PORT> -U <USER> -W --format=custom --no-acl --no-owner <DB_NAME> > (date -I)_poster.dump
```

#### Import DB dump
```
psql postgres://postgres:postgres@localhost:5432/postgres < /path/to/dump
```

## Top level files

### *.buildpacks*
Buildpacks are used when building slug for deployment. Below are some examples.

```
https://github.com/heroku/heroku-buildpack-apt
https://github.com/mojodna/heroku-buildpack-gdal.git
https://github.com/cyberdelia/heroku-geo-buildpack.git
https://github.com/heroku/heroku-buildpack-python.git#009d0ddb
https://github.com/heroku/heroku-buildpack-python.git
https://github.com/weibeld/heroku-buildpack-run.git
```

### *Aptfile*
 * used by *https://github.com/heroku/heroku-buildpack-apt*

Contains list of "to-be-installed" apt packages for the build.

### *buildpack-run.sh*
 * used by *https://github.com/weibeld/heroku-buildpack-run.git*

Contains shell script that will be run on build.

### *dcmanage.sh*
Shell wrapper for docker-compose commands that shoud be used to run "manage.py" commands
but on development docker environment

### *docker-compose.yml*
Basic docker-compose file used to spin up development environment.

### *example.env*
Example environment variable settings for the application.

### *manage.py*
Standard Django manage.py script
 * used by *https://github.com/heroku/heroku-buildpack-python.git*

### *Procfile*
Processes defined to be run on container deployment to server

### *Pipfile, Pipfile.lock*
Python dependencies file.
 * used by *https://github.com/heroku/heroku-buildpack-python.git*

### *runtime.txt*
Python runtime version dependency.
 * used by *https://github.com/heroku/heroku-buildpack-python.git*


## Windows quickstart

### install prerequisites
You need to have docker and docker-compose installed. They are bundled together
on windows.
Follow basic tutorial to setup Docker, Docker-compose and (Virtualbox)
https://docs.docker.com/docker-for-windows/install/

### preparation
After cloning repository you need to create custom .env file. Reasonable defaults
 are in example.env so just start with copying this file.

Then because of windows handling all stuff differently then normal OS, you need to
 specify path in the docker-compose-windows.yml. So edit line 15 `- //c/Users/<path to code>:/code` and
 change it to the path you have the source code. eg. `- //c/Users/Carl/code:/code`

Please note the forward slashes, `//` starting notation and the fact, that on Windows,
 you can only mount folders under `C:/Users` or you need to setup custom sharing in
 docker on Windows.

### The first run
During the first run the initial configuration is done on the background.
 This results in longer startup time. Please be patient.

Start docker containers with docker-compose.
Because windows have different settings for networking and stuff, there is second
 file that is used for configuration called `docker-compose-windows.yml`

Run basic command to spin up all required containers in first docker terminal:
```
docker-compose -f docker-compose-windows.yml up
```

This terminal needs to be running all the time. It displays log of all containers,
 which can be handy while debugging stuff. It takes some time to spin up all containers
 on the first run, so again, please be patient.

Then you can run second docker terminal to make maintenance of the application
 like creating database tables or creating local admin user so you can control the
 system.

Run these command in SECOND terminal
```
docker-compose -f docker-compose-windows.yml run --rm poster-web python manage.py migrate
docker-compose -f docker-compose-windows.yml run --rm poster-web python manage.py createsuperuser
```

### FAQ

#### Restarting web container
In some cases (during the first run mostly) it happens that web container will spin
 up faster than the database (Postgres) container. This results in error in the
 FIRST terminal. Don't stop that console - you just need to restart web container

So - To restart the web process container run in SECOND terminal:
```
docker-compose -f docker-compose-windows.yml restart poster-web
```
You can also see log changing in the FIRST terminal.

#### Stopping the docker
You can stop the docker containers by pressing CTRL+C in the FIRST terminal and waiting.
If you close that terminal it is possible that docker will keep running. In this case you can
use `down` command to stop all defined running containers.
```
docker-compose -f docker-compose-windows.yml down
```

#### Stopping containers and removing all the data
Stop running docker containers and remove all volumes (!!! This will clear the database !!! use with caution !)
```
docker-compose -f docker-compose-windows.yml down -v
```

#### Stop docker virtual machine on windows
Stop docker machine on Windows - otherwise it will require to Force-stop stuff while restarting the Windows machine.
```
docker-machine stop
```

## Troubleshooting

### Cannot run redis container (or others)
Arch linux (and probably some others) with linux kernel version 4.15.x+ (confirmed on 4.16.5) has an issue with running some older versions of containers (redis:3.0.0 in our case, also found mentions of CentOS 6, with CentOS 7 working).

* The fix is described in (https://bbs.archlinux.org/viewtopic.php?pid=1774110#p1774110), `vsyscall=emulate` needs to be added as a kernel parameter.
