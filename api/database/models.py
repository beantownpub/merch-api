import logging
from datetime import datetime

from .db import db


logging.info('WTF DB\n%s', db)
logging.info('WTF DB\n%s', dir(db))


class Inventory(db.Document):
    small = db.IntField(default=0)
    medium = db.IntField(default=0)
    large = db.IntField(default=0)
    xl = db.IntField(default=0)
    xxl = db.IntField(default=0)
    quantity = db.IntField(default=0)
    one_size = db.BooleanField(default=False)
    sizes = db.BooleanField()

    @property
    def total(self):
        if not self.one_size:
            total = self.small + self.medium + self.large + self.xl + self.xxl
        else:
            total = self.quantity
        return total


class Product(db.Document):
    name = db.StringField(max_length=120)
    category = db.StringField()
    description = db.StringField()
    price = db.FloatField()
    sku = db.IntField(unique=True)
    is_active = db.BooleanField(default=True)
    quantity = db.ReferenceField(Inventory)
    one_size = db.BooleanField()
    sizes = db.BooleanField()
    img_path = db.StringField()
    meta = {'allow_inheritance': True}

    @property
    def slug(self):
        slug = self.name.lower().replace(' ', '-')
        return slug


class CartItem(db.Document):
    item_count = db.IntField(default=1)
    time_added = db.DateTimeField(default=datetime.utcnow)
    item = db.ReferenceField(Product)
    cart_id = db.StringField(max_length=25)
    size = db.StringField(default='one_size')


class Cart(db.Document):
    cart_id = db.StringField(max_length=120, unique=True)
    time_created = db.DateTimeField(default=datetime.utcnow)
    cart_items = db.ListField(db.ReferenceField(CartItem))


class Customer(db.Document):
    first_name = db.StringField()
    last_name = db.StringField()
    info = db.DictField()


class Order(db.Document):
    customer = db.ReferenceField(Customer)
    cart = db.ReferenceField(Cart)
    completed = db.BooleanField(default=False)
