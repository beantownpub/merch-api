from datetime import datetime
from .pg_db import db


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean)
    price = db.Column(db.Float)
    category_id = db.Column(db.String, db.ForeignKey('category.name'), nullable=False)
    inventory_id = db.Column(db.String, db.ForeignKey('inventory.name'), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean)
    has_sizes = db.Column(db.Boolean)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return '<Category %r>' % self.name


class Inventory(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column(db.String(50), unique=True)
    small = db.Column(db.Integer, default=0)
    medium = db.Column(db.Integer, default=0)
    large = db.Column(db.Integer, default=0)
    xl = db.Column(db.Integer, default=0)
    xxl = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    has_sizes = db.Column(db.Boolean, default=False)
    product = db.relationship('Product', backref='inventory', lazy=True)

    @property
    def total(self):
        if not self.has_sizes:
            total = self.small + self.medium + self.large + self.xl + self.xxl
        else:
            total = self.quantity
        return total


class CartItem(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    item_count = db.Column(db.Integer, default=1)
    time_added = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='inventory', lazy=True)
    cart_id = db.Column(db.String, db.ForeignKey('cart.id'), nullable=False)
    size = db.Column(db.String(12), default='one_size')


class Cart(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    cart_items = db.relationship('Product', backref='category', lazy=True)
