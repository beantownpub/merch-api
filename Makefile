.PHONY: all test clean

name ?= merch_api
image ?= $(name)
repo ?= jalgraves
tag ?= $(shell yq eval '.info.version' swagger.yaml)

compile:
		cp requirements.txt prev-requirements.txt
		pip-compile requirements.in

build:
		@echo "\033[1;32m. . . Building Contact API image . . .\033[1;37m\n"
		docker build -t $(image):$(tag) .

publish: build
		docker tag $(image):$(tag) $(repo)/$(image):$(tag)
		docker push $(repo)/$(image):$(tag)

start:
		@echo "\033[1;32m. . . Starting Merch API container . . .\033[1;37m\n"
		docker run \
			--name merch_api \
			--restart always \
			-p "5000:5000" \
			-e MONGO_HOST=${mongo_host} \
			-e MONGO_PW=${BEANTOWN_MONGO_PW} \
			-e MONGO_USER='admin' \
			-e MONGO_DB='admin' \
			-e SESSION_KEY=${BEANTOWN_SESSION_KEY} \
			-e ORIGIN_URL='http://localhost:3000' \
			-e AUTH_DB=${AUTH_DB} \
			-e AUTH_DB_USER=${AUTH_DB_USER} \
			-e AUTH_DB_PW=${AUTH_DB_PW} \
			-e AUTH_DB_HOST=$(pg_host) \
			-e AUTH_API_KEY=${AUTH_API_KEY} \
			merch_api

stop:
		docker rm -f merch_api || true

mongo:
		@echo "\033[1;32m. . . Starting MongoDB container . . .\n"
		mkdir -p ${PWD}/data || true
		docker run \
			-d \
			-p 27017-27019:27017-27019 \
			-e MONGO_INITDB_ROOT_PASSWORD=${BEANTOWN_MONGO_PW} \
			-e MONGO_INITDB_ROOT_USERNAME=${MONGO_USER} \
			-v ${PWD}/data:/data/db \
			--name mongodb \
			--restart always \
			mongo:4.0.13-xenial

mongo_no_auth:
		@echo "\033[1;32m. . . Starting MongoDB container . . .\033[1;37m\n"
		mkdir -p ${PWD}/data || true
		docker run \
			-d \
			-p 27017-27019:27017-27019 \
			-v ${PWD}/data:/data/db \
			--name mongodb \
			--restart always \
			mongo:4.0.13-xenial

pg:
		docker run \
			--name pg \
			-p 5432:5432 \
			-e POSTGRES_PASSWORD=T84xcUb3jBrU6jHZLa29DP2muFGJ \
			postgres:13.1

clean:
		rm -rf api/__pycache__ || true
		rm .DS_Store || true
		rm api/*.pyc