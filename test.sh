#!/bin/bash

METHOD=${1}

curl \
    -v \
    -H "Content-Type: application/json" \
    -d '{"name": "guinness shirt", "is_active": true, "description": "Beantown Guinness Shirt", "category": "tshirts", "sku": 3, "price": 19.99}' \
    -X ${METHOD} \
    localhost:5000/v2/products
