import random

from .db_utils import get_item_from_db, run_db_action


class ParamArgs:
    def __init__(self, args):
        self.args = args
        self.cart_id = args.get('cart_id')

    def __repr__(self):
        return repr(self.map)

    @property
    def map(self):
        args_dict = {
            "cart_id": self.cart_id
        }
        return args_dict


def cart_item_to_dict(cart_item):
    item_data = {
        "quantity": cart_item.item_count,
        "sku": cart_item.product.id,
        "name": cart_item.product.name,
        "price": cart_item.product.price
    }
    item_data['total'] = item_data['quantity'] * item_data['price']
    return item_data


def generate_cart_id():
    """Generate and return a random cart_id"""
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    cart_id_length = 25
    for _ in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters) - 1)]
    return cart_id


def get_cart_items(cart_id):
    cart_data = {
        'cart_items': [],
        'cart_id': cart_id
    }
    cart = get_item_from_db('cart', query={"cart_id": cart_id})
    query = {"cart_id": cart.cart_id}
    cart_items = get_item_from_db('cart_item', query=query, multiple=True)
    for item in cart_items:
        if item.product:
            item_data = cart_item_to_dict(item)
            cart_data['cart_items'].append(item_data)
    cart_data['total'] = calculate_cart_total(cart)
    return cart_data


def calculate_cart_total(cart):
    item_prices = []
    cart_items = get_item_from_db('cart_item', query={"cart_id": cart.cart_id}, multiple=True)
    for item in cart_items:
        if item.product:
            item_count = item.item_count
            price = item.product.price
            item_prices.append(item_count * price)
    return round(sum(item_prices), 2)