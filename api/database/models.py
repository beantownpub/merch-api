from datetime import datetime
from .db import DB

from sqlalchemy.dialects.postgresql import JSON


customer_association = DB.Table('customer_association', DB.Model.metadata,
    DB.Column('customer_id', DB.Integer, DB.ForeignKey('customers.id')),
    DB.Column('order_id', DB.Integer, DB.ForeignKey('orders.id'))
)

order_association = DB.Table('order_association', DB.Model.metadata,
    DB.Column('order_item_id', DB.Integer, DB.ForeignKey('order_item.id')),
    DB.Column('order_id', DB.Integer, DB.ForeignKey('orders.id'))
)

product_association = DB.Table('product_association', DB.Model.metadata,
    DB.Column('product_id', DB.Integer, DB.ForeignKey('product.id')),
    DB.Column('cart_item_id', DB.Integer, DB.ForeignKey('cart_item.id')),
    DB.Column('order_item_id', DB.Integer, DB.ForeignKey('order_item.id'))
)

product_orders = DB.Table('product_orders', DB.Model.metadata,
    DB.Column('product_id', DB.Integer, DB.ForeignKey('product.id')),
    DB.Column('order_id', DB.Integer, DB.ForeignKey('orders.id'))
)


class Product(DB.Model):
    __tablename__ = 'product'
    id = DB.Column(DB.Integer, unique=True, primary_key=True)
    name = DB.Column(DB.String(50), unique=True)
    sku = DB.Column(DB.Integer, unique=True)
    description = DB.Column(DB.String)
    creation_date = DB.Column(DB.DateTime, default=datetime.utcnow)
    is_active = DB.Column(DB.Boolean)
    price = DB.Column(DB.Float)
    image_name = DB.Column(DB.String)
    image_path = DB.Column(DB.String)
    category_id = DB.Column(DB.String, DB.ForeignKey('category.name'), nullable=False)
    inventory_id = DB.Column(DB.String, DB.ForeignKey('inventory.name'), nullable=False)
    #slug = DB.Column(DB.String(50))
    #uuid = DB.Column(DB.String, unique=True)
    cart = DB.relationship('CartItem', backref='product', lazy=True)


class Category(DB.Model):
    __tablename__ = 'category'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    name = DB.Column(DB.String(50), unique=True)
    is_active = DB.Column(DB.Boolean)
    has_sizes = DB.Column(DB.Boolean)
    products = DB.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return '<Category %r>' % self.name


class Inventory(DB.Model):
    __tablename__ = 'inventory'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    name = DB.Column(DB.String(50), unique=True)
    small = DB.Column(DB.Integer, default=0)
    medium = DB.Column(DB.Integer, default=0)
    large = DB.Column(DB.Integer, default=0)
    xl = DB.Column(DB.Integer, default=0)
    xxl = DB.Column(DB.Integer, default=0)
    quantity = DB.Column(DB.Integer, default=0)
    has_sizes = DB.Column(DB.Boolean, default=False)
    product = DB.relationship('Product', backref='inventory', lazy=True, uselist=False)

    @property
    def total(self):
        if not self.has_sizes:
            total = self.small + self.medium + self.large + self.xl + self.xxl
        else:
            total = self.quantity
        return total


class CartItem(DB.Model):
    __tablename__ = 'cart_item'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    item_count = DB.Column(DB.Integer, default=1)
    time_added = DB.Column(DB.DateTime, default=datetime.utcnow)
    cart_id = DB.Column(DB.String, DB.ForeignKey('cart.cart_id'), nullable=False)
    size = DB.Column(DB.String, unique=False)
    product_id = DB.Column(DB.String, DB.ForeignKey('product.name'), nullable=False)


class Cart(DB.Model):
    __tablename__ = 'cart'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    cart_id = DB.Column(DB.String, unique=True)
    time_created = DB.Column(DB.DateTime, default=datetime.utcnow)
    items = DB.relationship('CartItem', backref='cart', lazy=True, uselist=True)


class Address(DB.Model):
    __tablename__ = 'address'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    street = DB.Column(DB.String(150))
    unit = DB.Column(DB.String(150))
    city = DB.Column(DB.String(150))
    state = DB.Column(DB.String(150))
    zip_code = DB.Column(DB.String(12))


class Customer(DB.Model):
    __tablename__ = 'customers'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    first_name = DB.Column(DB.String(50))
    last_name = DB.Column(DB.String(50))
    email_address = DB.Column(DB.String(60), unique=True)
    phone_number = DB.Column(DB.String(15))
    address = DB.Column(DB.Integer, DB.ForeignKey('address.id'), nullable=False)
    orders = DB.Column(JSON, default=[])


class OrderItem(DB.Model):
    __tablename__ = 'order_item'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    item_count = DB.Column(DB.Integer, default=1)
    time_added = DB.Column(DB.DateTime, default=datetime.utcnow)
    cart_id = DB.Column(DB.String, unique=False)
    product = DB.relationship('Product', backref='order_item', secondary=product_association, uselist=False)
    order = DB.relationship('Order', backref='order', secondary=order_association, sync_backref=False, viewonly=True, uselist=False)


class Order(DB.Model):
    __tablename__ = 'orders'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    customer = DB.Column(DB.String, DB.ForeignKey('customers.email_address'), nullable=False)
    cart_id = DB.Column(DB.String, unique=False)
    completed = DB.Column(DB.Boolean, default=False)
    time_created = DB.Column(DB.DateTime, default=datetime.utcnow)
    items = DB.Column(JSON)
    status = DB.Column(DB.Enum('received','pending', 'completed', 'cancelled', name="statuses"), default="pending")
