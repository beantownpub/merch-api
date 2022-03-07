# Merch API
Flask REST API for **[beantownpub.com's](https://beantownpub.com)** online retail sales

[![CircleCI](https://circleci.com/gh/beantownpub/merch_api/tree/master.svg?style=svg)](https://circleci.com/gh/beantownpub/merch_api/tree/master)


## Example Requests

GET product

```shell
http 'localhost:5000/v2/products?name=umbrella&location=beantown'
```

GET category

```shell
http 'localhost:5000/v2/categories?name=tshirts&location=beantown'
```