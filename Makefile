.PHONY: all test clean

name ?= merch-api
image ?= $(name)
repo ?= jalgraves
tag ?= $(shell yq eval '.info.version' swagger.yaml)
hash = $(shell git rev-parse --short HEAD)

ifeq ($(env),dev)
	image_tag = $(tag)-$(hash)
else
	image_tag = $(tag)
endif

compile:
	cp requirements.txt prev-requirements.txt
	pip-compile requirements.in

build:
	@echo "\033[1;32m. . . Building Contact API image . . .\033[1;37m\n"
	docker build -t $(image):$(image_tag) .

publish: build
	docker tag $(image):$(image_tag) $(repo)/$(image):$(image_tag)
	docker push $(repo)/$(image):$(image_tag)

clean:
	rm -rf api/__pycache__ || true
	rm .DS_Store || true
	rm api/*.pyc