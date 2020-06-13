.PHONY: all test clean

build:
		@echo "\033[1;32m. . . Building Merch API image . . .\033[1;37m\n"
		docker build -t merch_api .

build_no_cache:
		docker build -t merch_api . --no-cache=true

publish: build
		docker tag merch_api jalgraves/merch_api
		docker push jalgraves/merch_api

start:
		@echo "\033[1;32m. . . Starting Merch API container . . .\033[1;37m\n"
		docker run \
			--name merch_api \
			--restart always \
			-p "5000:5000" \
			-e MONGO_HOST=${MONGO_REMOTE} \
			-e MONGO_PW=${BEANTOWN_MONGO_PW} \
			-e MONGO_USER='admin' \
			-e MONGO_DB='admin' \
			-e SESSION_KEY=${BEANTOWN_SESSION_KEY} \
			merch_api

stop:
		docker rm -f merch_api || true

redis:
		docker run -d --name red -p "6379:6379" --restart always redis

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

clean:
		rm -rf api/__pycache__ || true
		rm .DS_Store || true
		rm api/*.pyc