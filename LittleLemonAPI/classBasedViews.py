from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .models import *
from .serializers import *
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


# CLASS-BASED VIEWS

# 1) Categories and single category
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        elif self.request.method == "POST":
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["PUT", "DELETE", "PATCH"]:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]
    

# 2) Menu items and single menu item
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        elif self.request.method == "POST":
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        elif self.request.method in ["PUT", "DELETE", "PATCH"]:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]
        
        
# 3) Manager Group
class ManagersView(generics.ListCreateAPIView):
    queryset = Group.objects.filter(name="Manager")
