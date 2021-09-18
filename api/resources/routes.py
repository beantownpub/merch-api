from .product import ProductsAPI, CategoryAPI
from .products import ProdAPI, ProdsAPI
from .product_categories import CategoriesAPI, CatAPI
from .cart import CartAPI
from .orders import OrdersAPI
from .auth import AuthAPI


def init_routes(api):
    api.add_resource(ProductsAPI, '/v1/merch/products')
    api.add_resource(CategoryAPI, '/v1/merch/products/<category>')
    api.add_resource(CartAPI, '/v1/merch/cart')
    api.add_resource(OrdersAPI, '/v1/merch/orders')
    api.add_resource(AuthAPI, '/v1/auth')
    api.add_resource(ProdAPI, '/v2/products')
    api.add_resource(CatAPI, '/v1/categories/<category>')
    api.add_resource(ProdsAPI, '/v2/products/<category>')
    api.add_resource(CategoriesAPI, '/v1/categories')
