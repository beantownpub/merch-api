.PHONY: all test clean

name ?= merch-api
image ?= $(name)
port ?= 5000
repo ?= jalgraves
tag ?= $(shell yq eval '.info.version' swagger.yaml)
hash = $(shell git rev-parse --short HEAD)

ifeq ($(env),dev)
	image_tag = $(tag)-$(hash)
	context = ${DEV_CONTEXT}
	namespace = ${DEV_NAMESPACE}
else ifeq ($(env),prod)
    image_tag = $(tag)
	context = ${PROD_CONTEXT}
	namespace = ${PROD_NAMESPACE}
else
	env := dev
endif

context:
	kubectl config use-context $(context)

compile:
	cp requirements.txt prev-requirements.txt
	pip-compile requirements.in

build:
	@echo "\033[1;32m. . . Building Merch API image . . .\033[1;37m\n"
	docker build -t $(image):$(image_tag) .

publish: build
	docker tag $(image):$(image_tag) $(repo)/$(image):$(image_tag)
	docker push $(repo)/$(image):$(image_tag)

clean:
	rm -rf api/__pycache__ || true
	rm .DS_Store || true
	rm api/*.pyc

kill_pod: context
	${HOME}/github/helm/scripts/kill_pod.sh $(env) $(name)

kill_port_forward: context
	${HOME}/github/helm/scripts/stop_port_forward.sh $(port)

redeploy: build restart

restart: kill_pod kill_port_forward

seed:
	python3 bin/seed_products.py --env $(env)

reset_db: context
	${HOME}/github/helm/scripts/kill_pod.sh ${DATABASE_NAMESPACE} postgres
