from .products import ProductAPI, ProductsAPI
from .product_categories import CategoriesAPI, CategoryAPI
from .cart import CartAPI, CheckoutAPI
from .orders import OrdersAPI, OrderAPI
from .healthcheck import HealthCheckAPI
from .merch import MerchAPI

product_routes = [
    '/v1/merch/products',
    '/v1/merch/categories',
    '/v2/categories'
]

def init_routes(api):
    api.add_resource(HealthCheckAPI, '/v1/merch/healthz')
    api.add_resource(ProductsAPI, '/v1/merch/products')
    api.add_resource(CategoryAPI, *product_routes)
    api.add_resource(CartAPI, '/v1/merch/cart')
    api.add_resource(OrdersAPI, '/v1/merch/orders')
    api.add_resource(OrderAPI, '/v1/merch/orders/<order_id>')
    api.add_resource(ProductAPI, '/v2/products')
    api.add_resource(CategoriesAPI, '/v1/categories')
    api.add_resource(CheckoutAPI, '/v2/cart/empty')
    api.add_resource(MerchAPI, '/v2/merch')
