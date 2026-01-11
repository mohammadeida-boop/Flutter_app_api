# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *
from django.contrib.auth.hashers import make_password

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'phone', 'address', 'created_at']
        read_only_fields = ['user_id', 'created_at']

# User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'address', 'password']
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("بيانات الدخول غير صحيحة")

# Restaurant Serializer
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

# Menu Serializer
class MenuSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')
    
    class Meta:
        model = Menu
        fields = '__all__'

# OrderItem Serializer (Nested)
class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='menu_item.item_name')
    item_price = serializers.ReadOnlyField(source='menu_item.price')
    
    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'menu_item', 'item_name', 'item_price', 'quantity', 'price']

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'order_id', 'user', 'user_email', 'restaurant', 'restaurant_name',
            'order_status', 'total_amount', 'created_at', 'items'
        ]
        read_only_fields = ['order_id', 'created_at']

# Create Order Serializer
class CreateOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['restaurant', 'total_amount', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order

# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

# Driver Serializer
class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

# Delivery Serializer
class DeliverySerializer(serializers.ModelSerializer):
    driver_name = serializers.ReadOnlyField(source='driver.name')
    order_id = serializers.ReadOnlyField(source='order.order_id')
    
    class Meta:
        model = Delivery
        fields = '__all__'

# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.name')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')
    
    class Meta:
        model = Review
        fields = '__all__'