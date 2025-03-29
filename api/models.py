from mongoengine import (
    Document, EmbeddedDocument, StringField, EmailField, ReferenceField, 
    ListField, BooleanField, IntField, DecimalField, DateTimeField, 
    EmbeddedDocumentListField, URLField, CASCADE, ObjectIdField
)
from django.contrib.auth.hashers import make_password, check_password
from bson import ObjectId


class User(Document):
    meta = {'collection': 'users'}
    # id = ObjectIdField(primary_key=True)
    email = EmailField(unique=True, required=True)
    password = StringField(required=True)
    is_admin = BooleanField(default=False)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True  

    @property
    def is_staff(self):
        return self.is_admin     

    @property
    def is_superuser(self):
        return self.is_admin   

class Category(Document):
    # id = ObjectIdField(primary_key=True)
    name = StringField(required=True, unique=True)
    description = StringField()
    
    meta = {'collection': 'categories'}

    def __str__(self):
        return self.name

class Product(Document):
    # id = ObjectIdField(primary_key=True)
    name = StringField(required=True, unique=True)
    description = StringField()
    category = ReferenceField(Category, required=True, reverse_delete_rule=CASCADE)
    price = DecimalField(required=True, precision=2)
    stock = IntField(default=0)
    images = ListField(URLField())
    
    meta = {'collection': 'products'}

class CartItem(EmbeddedDocument):
    # id = ObjectIdField(primary_key=True)
    product = ReferenceField(Product, required=True)
    quantity = IntField(default=1)

class Cart(Document):
    # id = ObjectIdField(primary_key=True)
    user = ReferenceField(User, required=True, unique=True)
    items = EmbeddedDocumentListField(CartItem)
    
    meta = {'collection': 'carts'}

class OrderItem(EmbeddedDocument):
    # id = ObjectIdField(primary_key=True)
    product = ReferenceField(Product, required=True)
    quantity = IntField(default=1)
    price = DecimalField(required=True, precision=2)

class Order(Document):
    STATUS_CHOICES = ('Pending', 'Shipped', 'Delivered', 'Cancelled')

    # id = ObjectIdField(primary_key=True)
    user = ReferenceField(User, required=True)
    items = EmbeddedDocumentListField(OrderItem)
    total_price = DecimalField(required=True, precision=2)
    status = StringField(choices=STATUS_CHOICES, default='Pending')
    created_at = DateTimeField(auto_now_add=True)
    
    meta = {'collection': 'orders'}

class Coupon(Document):
    # id = ObjectIdField(primary_key=True)
    code = StringField(required=True, unique=True)
    discount_percentage = IntField(required=True, min_value=1, max_value=100)
    expiry_date = DateTimeField(required=True)
    usage_limit = IntField(default=1)
    
    meta = {'collection': 'coupons'}
