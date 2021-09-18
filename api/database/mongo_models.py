import logging
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from .db import db


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
    img_name = db.StringField()
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


class Address(db.Document):
    street = db.StringField(max_length=220)
    city = db.StringField(max_length=120)
    state = db.StringField(max_length=120)
    zip_code = db.StringField(max_length=5)


class Customer(db.Document):
    first_name = db.StringField()
    last_name = db.StringField()
    address = db.ReferenceField(Address)
    info = db.DictField()


class Order(db.Document):
    customer = db.ReferenceField(Customer)
    cart = db.ReferenceField(Cart)
    completed = db.BooleanField(default=False)
    nonce = db.StringField(max_length=120, unique=True)
    time_created = db.DateTimeField(default=datetime.utcnow)


class User(db.Document):
    username = db.StringField(max_length=56, unique=True)
    password_hash = db.StringField(max_length=128, min_length=8, unique=True)

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            'SECRET_KEY', algorithm='HS256')
