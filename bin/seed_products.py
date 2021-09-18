import json
import sys
import requests


def get_products():
    with open('./api/products.json') as f:
        products = json.load(f)
    return products


def post_item(menu_item):
    url = 'http://localhost:5000/v1/merch/products'
    r = requests.post(url, json=menu_item)
    if r.status_code != 200:
        print(r.content)
    else:
        print("OK")


def put_item(menu_item):
    url = 'http://localhost:5000/v1/merch/products'
    r = requests.put(url, json=menu_item)
    if r.status_code != 200:
        print(r.content)
    else:
        print("OK")


def delete_item(menu_item):
    url = 'http://localhost:5000/v1/merch/items'
    r = requests.delete(url, json=menu_item)
    print(r.status_code)


if __name__ == '__main__':
    print(__file__)
    menu = get_products()
    sections = menu['categories'].keys()
    for section in sections:
        items = menu['categories'][section]
        for i in items:
            if sys.argv[1] == 'add':
                post_item(i)
            elif sys.argv[1] == 'update':
                put_item(i)
            else:
                delete_item(i)
