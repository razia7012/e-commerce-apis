from rest_framework import serializers
from bson import ObjectId
from .models import User, Product, Category, Order, Coupon


class ObjectIdField(serializers.Field):
    """ Serializer field to handle MongoDB ObjectId """

    def to_internal_value(self, data):
        try:
            return ObjectId(data)
        except:
            raise serializers.ValidationError("Invalid ObjectId format")

    def to_representation(self, value):
        return str(value)

class UserSerializer(serializers.Serializer):
    id = ObjectIdField(read_only=True) 
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    is_admin = serializers.BooleanField(default=False)

    def create(self, validated_data):
        if User.objects(email=validated_data["email"]).first():
            raise serializers.ValidationError({"error": "User with this email already exists"})

        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)  
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField()  
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField(default=0)
    images = serializers.ListField(child=serializers.URLField(), required=False)

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        category = Category.objects(id=category_id).first() 
        if not category:
            raise serializers.ValidationError("Invalid category ID")

        product = Product(**validated_data, category=category)
        product.save()
        return product

    def update(self, instance, validated_data):
        if "category" in validated_data:
            category_id = validated_data.pop("category")
            category = Category.objects(id=category_id).first()
            if not category:
                raise serializers.ValidationError("Invalid category ID")
            instance.category = category 

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance

class CategorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)  
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        category = Category(**validated_data)
        category.save()
        return category

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CartItemSerializer(serializers.Serializer):
    product = serializers.CharField()  
    quantity = serializers.IntegerField(min_value=1)

    def validate_product(self, value):
        if not Product.objects(id=value).first():
            raise serializers.ValidationError("Invalid product ID.")
        return value

class CartSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)
    items = CartItemSerializer(many=True)

class OrderItemSerializer(serializers.Serializer):
    product = serializers.CharField()  
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)  
    items = OrderItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, default="Pending")
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user  
        items_data = validated_data.pop('items')
        total_price = sum(item['quantity'] * item['price'] for item in items_data)
        order = Order(user=user, items=items_data, total_price=total_price)
        order.save()
        return order

class CouponSerializer(serializers.Serializer):
    code = serializers.CharField()
    discount_percentage = serializers.IntegerField()
    expiry_date = serializers.DateTimeField()
    usage_limit = serializers.IntegerField(default=1)

    def validate_code(self, value):
        if not Coupon.objects(code=value).first():
            raise serializers.ValidationError("Invalid coupon code.")
        return value

class CouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    discount_percentage = serializers.IntegerField(min_value=1, max_value=100)
    expiry_date = serializers.DateTimeField()
    usage_limit = serializers.IntegerField(default=1)

    def create(self, validated_data):
        return Coupon.objects.create(**validated_data)
