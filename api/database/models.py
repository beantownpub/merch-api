from datetime import datetime
from .db import db

from sqlalchemy.dialects.postgresql import JSON


cart_association = db.Table('cart_association', db.Model.metadata,
    db.Column('cart_item_id', db.Integer, db.ForeignKey('cart_item.id')),
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'))
)

customer_association = db.Table('customer_association', db.Model.metadata,
    db.Column('customer_id', db.Integer, db.ForeignKey('customers.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'))
)

order_association = db.Table('order_association', db.Model.metadata,
    db.Column('order_item_id', db.Integer, db.ForeignKey('order_item.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'))
)

product_association = db.Table('product_association', db.Model.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('cart_item_id', db.Integer, db.ForeignKey('cart_item.id')),
    db.Column('order_item_id', db.Integer, db.ForeignKey('order_item.id'))
)

product_orders = db.Table('product_orders', db.Model.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'))
)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    sku = db.Column(db.Integer, unique=True)
    description = db.Column(db.String)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean)
    price = db.Column(db.Float)
    image_name = db.Column(db.String)
    image_path = db.Column(db.String)
    category_id = db.Column(db.String, db.ForeignKey('category.name'), nullable=False)
    inventory_id = db.Column(db.String, db.ForeignKey('inventory.name'), nullable=False)
    cart = db.relationship('CartItem', backref='product', lazy=True)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean)
    has_sizes = db.Column(db.Boolean)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return '<Category %r>' % self.name


class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column(db.String(50), unique=True)
    small = db.Column(db.Integer, default=0)
    medium = db.Column(db.Integer, default=0)
    large = db.Column(db.Integer, default=0)
    xl = db.Column(db.Integer, default=0)
    xxl = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    has_sizes = db.Column(db.Boolean, default=False)
    product = db.relationship('Product', backref='inventory', lazy=True, uselist=False)

    @property
    def total(self):
        if not self.has_sizes:
            total = self.small + self.medium + self.large + self.xl + self.xxl
        else:
            total = self.quantity
        return total


class CartItem(db.Model):
    __tablename__ = 'cart_item'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    item_count = db.Column(db.Integer, default=1)
    time_added = db.Column(db.DateTime, default=datetime.utcnow)
    cart_id = db.Column(db.String, unique=False)
    product_id = db.Column(db.String, db.ForeignKey('product.name'), nullable=False)
    cart = db.relationship('Cart', backref='cart', secondary=cart_association, sync_backref=False, viewonly=True, uselist=False)


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    cart_id = db.Column(db.String, unique=True)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.Column(JSON, default=[])


class Address(db.Model):
    __tablename__ = 'address'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    street = db.Column(db.String(150))
    unit = db.Column(db.String(150))
    city = db.Column(db.String(150))
    state = db.Column(db.String(150))
    zip_code = db.Column(db.String(12))


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email_address = db.Column(db.String(60), unique=True)
    phone_number = db.Column(db.String(15))
    address = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    orders = db.Column(JSON, default=[])


class OrderItem(db.Model):
    __tablename__ = 'order_item'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    item_count = db.Column(db.Integer, default=1)
    time_added = db.Column(db.DateTime, default=datetime.utcnow)
    cart_id = db.Column(db.String, unique=False)
    product = db.relationship('Product', backref='order_item', secondary=product_association, uselist=False)
    order = db.relationship('Order', backref='order', secondary=order_association, sync_backref=False, viewonly=True, uselist=False)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    customer = db.Column(db.String, db.ForeignKey('customers.email_address'), nullable=False)
    cart_id = db.Column(db.String, unique=False)
    completed = db.Column(db.Boolean, default=False)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.Column(JSON)
    status = db.Column(db.Enum('received','pending', 'completed', 'cancelled', name="statuses"), default="pending")
