.PHONY: test

start:
	docker-compose up

start-d:
	docker-compose up -d

stop:
	docker-compose stop

restart:
	docker-compose up --force-recreate --no-deps -d poster-web poster-celery_beat poster-celery_worker

rebuild-and-restart:
	docker-compose build poster-web
	docker-compose up --force-recreate --no-deps -d poster-web poster-celery_beat poster-celery_worker

restart-celery:
	docker-compose rm -fsv poster-flower
	docker-compose rm -fsv poster-celery_beat
	docker-compose rm -fsv poster-celery_worker
	docker-compose rm -fsv poster-redis
	docker-compose up --no-deps -d poster-redis
	docker-compose up --no-deps -d poster-celery_worker
	docker-compose up --no-deps -d poster-celery_beat
	docker-compose up --no-deps -d poster-flower

stop-all-docker-containers:
	docker stop $$(docker ps -q)

remove-all-docker-containers:
	docker rm $$(docker ps -aq)

stop-and-remove-all-docker-containers:
	docker stop $$(docker ps -q)
	docker rm $$(docker ps -aq)

