#!/bin/bash

METHOD=${1}

curl \
    -v \
    -H "Content-Type: application/json" \
    -d '{"name": "tshirts", "is_active": true, "has_sizes": true}' \
    -X ${METHOD} \
    localhost:5000/v1/categories/tshirts

curl \
    -v \
    -H "Content-Type: application/json" \
    -d '{"name": "hats", "is_active": true, "has_sizes": false}' \
    -X ${METHOD} \
    localhost:5000/v1/categories/hats

curl \
    -v \
    -H "Content-Type: application/json" \
    -d '{"name": "drinkware", "is_active": true, "has_sizes": false}' \
    -X ${METHOD} \
    localhost:5000/v1/categories/drinkware
