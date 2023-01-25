from rest_framework import serializers
from django.contrib.auth.models import Group, User
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug"]


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "category_id", "category", "featured"]
        

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name"]
        
        
class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "groups"]


class DeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username","first_name", "last_name"]
        
        
class DeliveryPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
    
    
class CartSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    item = serializers.CharField(source="menuitem.title")
    
    class Meta:
        model = Cart
        fields = ["username", "item", "unit_price", "quantity", "price"]


class OrderItemSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="menuitem.title")
    
    class Meta:
        model = OrderItem
        fields = ["item", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    delivery_status = serializers.BooleanField(source="status")
    delivery_person = DeliveryPersonSerializer(source="delivery_crew")
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2, source="total")
    
    orderitem = OrderItemSerializer(many=True, read_only=True, source="order")
    
    class Meta:
        model = Order
        fields = ["id", "username", "date", "total_price", "delivery_person", "delivery_status", "orderitem"]