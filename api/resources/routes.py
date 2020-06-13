from .product import ProductsAPI, CategoryAPI
from .cart import CartAPI


def init_routes(api):
    api.add_resource(ProductsAPI, '/v1/merch/products')
    api.add_resource(CategoryAPI, '/v1/merch/products/<category>')
    api.add_resource(CartAPI, '/v1/merch/cart')
