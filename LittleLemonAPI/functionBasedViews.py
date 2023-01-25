from django.shortcuts import  get_object_or_404
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from .models import *
from .serializers import *
from .permissions import IsManager, IsCustomer
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import datetime as dt
  

# FUNCTION BASED VIEWS

# 1) Categories and single category
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def categories(request):
    if request.method == "GET":
        items = Category.objects.all()
        serialized_items = CategorySerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
        
    elif request.method == "POST":
        if request.user.is_superuser:
            serialized_item = CategorySerializer(data=request.data)
            serialized_item.is_valid()
            serialized_item.save()
            return Response(serialized_item.validated_data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Unauthorized action"}, status=status.HTTP_403_FORBIDDEN)

    return Response({"message": "Error occurs"}, status=status.HTTP_404_NOT_FOUND)
     
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def category(request, pk):
    try:
        item =  get_object_or_404(Category, pk=pk)
    except:
        return Response({"message": f"Error occurs. There is no category with id = {pk}"}, status=status.HTTP_404_NOT_FOUND)
    
    # Or 
    # item =  get_object_or_404(Category, pk=pk)

    if request.method == "GET":
        serialized_item = CategorySerializer(item)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    
    elif  request.method in ["DELETE", "PUT"]:
        if request.user.is_superuser:
            if request.method == "DELETE":
                item.delete()
                return Response({"message": "Category deleted"}, status=status.HTTP_200_OK)
            
            elif request.method == "PUT":
                serialized_item = CategorySerializer(item, data=request.data);
                if serialized_item.is_valid():
                    serialized_item.save()
                    return Response(serialized_item.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Unauthorized action"}, status=status.HTTP_403_FORBIDDEN)



# 2) Menu items and single menu item
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.select_related('category').all()
        
        # Every user can paginate, sort and filter items
        # Filtering
        category_name = request.query_params.get('category')
        if category_name:
            items = items.filter(category__title=category_name)
            
        # Searching
        search_item = request.query_params.get("search")
        if search_item:
            items = items.filter(title__icontains=search_item)
        
        # Sorting
        sort = request.query_params.get("sort")
        if sort:
            items = items.order_by(sort) 
            
        # Pagination
        # if there is page or per-page queries than pagination will be applied
        # else without query all items will be displayed
        if request.query_params.get("per-page") or request.query_params.get("page"):
            per_page = request.query_params.get("per-page", default=4)
            page = request.query_params.get("page", default=1)            
            paginator = Paginator(items, per_page=per_page)
        
            try:
                items = paginator.page(number=page)
            except EmptyPage:
                items = []
        
        serialized_items = MenuItemSerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        if request.user.is_superuser:
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid()
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Unauthorized action"}, status=status.HTTP_403_FORBIDDEN)            

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def single_menu_item(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    
    if request.method == "GET":
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    
    elif request.method in ["PUT", "PATCH", "DELETE"]:
        # Admin can delete and update menu item
        if request.user.is_superuser:
            if request.method == "DELETE":
                item.delete()
                return Response({"message": "Menu item deleted"}, status=status.HTTP_200_OK)
            
            elif request.method == "PATCH" or request.method == "PUT":
                serializered_item = MenuItemSerializer(item, data=request.data, partial=True)
                if serializered_item.is_valid():
                    serializered_item.save()
                    return Response(data=serializered_item.data, status=status.HTTP_200_OK)
         
        # Manager can update featured        
        elif request.user.groups.filter(name="Manager").exists() and request.method == "PATCH":
            if 'featured' in request.data and request.data['featured'].lower() in ["true", "false"]:
                serializered_item = MenuItemSerializer(item, data=request.data, partial=True)
                if serializered_item.is_valid():
                    serializered_item.save()
                    return Response(data=serializered_item.data, status=status.HTTP_200_OK)
            
            else:     
                return Response({"message": "You can only change/update featured field!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Unauthorized action"}, status=status.HTTP_403_FORBIDDEN)  



# 3) Cart
@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsCustomer])
def cart(request):
    customer = request.user
    items = Cart.objects.filter(user=customer)
    
    if request.method == "GET":
        serialized_items = CartSerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    elif request.method in ["POST", "PATCH"]:
        menu_item_title = request.data["item"]
        menuitem = get_object_or_404(MenuItem, title=menu_item_title)
        
        # Quantity needs to be positiv integer:
        try:
            quantity = int(request.data["quantity"])
            if quantity <= 0:
                raise
        except:
            return Response({"message": "You typed invalid quanitity value!"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Creating new Cart object
        if request.method == "POST":
            # If cart is empty or menu is not already in the cart, item will be added to the cart:
            try:
                if len(items) == 0:
                    raise
                # If item already in the cart appropriate message is written
                if Cart.objects.get(user=customer, menuitem=menuitem):
                    return Response({"message": f"{menu_item_title} already in the cart."}, status=status.HTTP_400_BAD_REQUEST)
            except:
                cart = Cart.objects.create(user=customer, menuitem=menuitem, quantity=int(request.data["quantity"]))
            
        
        # Update-ing cart object - changeing quantity of the item
        else:
            cart = Cart.objects.get(user=customer, menuitem=menuitem)
            cart.quantity = quantity
            
        serialized_item = CartSerializer(cart)
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)
    
    elif request.method == "DELETE":
        items.delete()
        return Response({"message": f"All menu items deleted from the cart"}, status=status.HTTP_200_OK)
        
       
        
# 4) Orders
@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def orders(request):
    user_is_customer = request.user.groups.filter(name="Customer").exists()
    user_is_manager = request.user.groups.filter(name="Manager").exists()
    user_is_delivery_crew = request.user.groups.filter(name="Delivery Crew").exists()
    
    # Customer can do next things
    if user_is_customer:
        customer = request.user
        
        # Getting all order from single user
        if request.method == "GET":
            orders = Order.objects.filter(user=customer)
            serialized_items = OrderSerializer(orders, many=True)
            return Response(serialized_items.data, status=status.HTTP_200_OK)
        
        elif request.method == "POST":
            cart_items = Cart.objects.filter(user=customer)
            # Checking whether cart is empty
            if len(cart_items) == 0:
                return Response({"username": f"{customer.username}", "message": f"No items in the cart"}, status=status.HTTP_404_NOT_FOUND)
            
            order = Order.objects.create(user=customer, date=dt.datetime.now())
            total_price = 0
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price)
                
                total_price += cart_item.price
            
            # Total price of the whole order
            order.total = total_price
            order.save()
            # Deleting everything from cart
            cart_items.delete()
            
            serializered_item = OrderSerializer(order)
            
            return Response(serializered_item.data, status=status.HTTP_201_CREATED)
        
        elif request.method == "PUT":
            pass
        
    if user_is_manager:
        # Getting all order from all users
        if request.method == "GET":
            orders = Order.objects.all()
            serialized_items = OrderSerializer(orders, many=True)
            return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    if user_is_delivery_crew:
        if request.method == "GET":
            delivery_person = request.user
            orders = Order.objects.filter(delivery_crew=delivery_person)
            serialized_items = OrderSerializer(orders, many=True)
            return Response(serialized_items.data, status=status.HTTP_200_OK)
    
@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def order(request, pk):
    user_is_customer = request.user.groups.filter(name="Customer").exists()
    user_is_manager = request.user.groups.filter(name="Manager").exists()
    user_is_delivery_crew = request.user.groups.filter(name="Delivery Crew").exists()

    # Customer can access only order related to him
    if user_is_customer:
        customer = request.user
        order = get_object_or_404(Order, user=customer, pk=pk)
    
    # Manager can access every single order
    elif user_is_manager:
        order = get_object_or_404(Order, pk=pk)
        
    # Delivery crew can access only order related to him
    elif user_is_delivery_crew:
        delivery_person = request.user
        order = get_object_or_404(Order, delivery_crew=delivery_person, pk=pk)
        
        
    if request.method == "GET":
        serialized_item = OrderSerializer(order)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
        
    # Changing delivery status - everyone can change delivery status
    elif request.method == "PATCH":
        try:
            delivery_status = request.data["status"]
            
            if delivery_status.lower() == "true":
                order.status = True
            elif delivery_status.lower() == "false":  
                order.status = False
            else:
                return Response({"message" : "Delivery status can be true or false only"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            None
            
        # Manager can assign order to specific delivery member:
        if user_is_manager:
            try:
                username = request.data["delivery_username"]
                try:
                    delivery_person = User.objects.get(username=username)
                    order.delivery_crew = delivery_person
                except:
                    all_delivery_persons = User.objects.filter(groups__name="Delivery Crew")
                    serialized_items = DeliveryCrewSerializer(all_delivery_persons, many=True)
                    json = {}
                    json["message"] = "Here is the list of all available delivery crew members"
                    json["delivery_crew"] = serialized_items.data
                    return Response(json, status=status.HTTP_400_BAD_REQUEST)
            except:
                None
                
        order.save()
        serialized_item = OrderSerializer(order)
        return Response(serialized_item.data, status=status.HTTP_200_OK)

    # Only manager can delete order
    elif request.method == "DELETE" and user_is_manager:
        order.delete()
        return Response({"message" : "Order has been deleted"}, status=status.HTTP_200_OK)
         
            
        
# 5) User registration
@api_view(["POST", "GET"])
def user_registration(request):
    if request.method == "POST":
        username = request.data["username"]
        password = request.data["password"]
        email = request.data["email"]
        
        if not username or len(username) < 4:
            return Response({"message": "Username cannot be blank or less than 4 characters"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not password or len(password) < 6:
            return Response({"message": "Password needs to have at least 6 characters"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not email or not ".com" in email or not "@" in email:
            return Response({"message": "You didn't enter correct mail"}, status=status.HTTP_400_BAD_REQUEST)
        
        new_user = User.objects.create(username=username, password=password, email=email)
        # Default group for every new user is Customer
        new_user.groups.add(Group.objects.get(name="Customer"))
        
        serializered_item = UserSerializer(new_user)
        return Response(serializered_item.data, status=status.HTTP_201_CREATED)
    
    elif request.method == "GET" and request.user.is_superuser:
        all_users = User.objects.all()
        serialized_items = UserSerializer(all_users, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)

        
        
# 6) Manager group and single manager
@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def managers(request):
    if request.method == "GET":
        managers = User.objects.filter(groups__name="Manager")
        serialized_items = UserSerializer(managers, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        username = request.data['username']
        user = User.objects.get(username=username)
        
        group = Group.objects.get(name="Manager")
        group.user_set.add(user)
        return Response({"message": f"Manager {username} is created"}, status=status.HTTP_201_CREATED)

@api_view(["GET", "DELETE"])
@permission_classes([IsAdminUser])
def manager(request, pk):
    manager = get_object_or_404(User, id=pk, groups__name="Manager")
    # manager = User.objects.filter(groups__name="Manager", pk=pk)
    
    if request.method == "GET":
        serialized_item = UserSerializer(manager)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        group = Group.objects.get(name="Manager")
        group.user_set.remove(manager)
        return Response({"message": f"User {manager.username} is deleted from Manager group"}, status=status.HTTP_200_OK)



# 7) Delivery Crew group and single delivery_crew_member  
# Manager and admin can acces these methods
@api_view(["GET", "POST"])
@permission_classes([IsManager | IsAdminUser])
def delivery_crew(request):
    if request.method == "GET":
        crew = User.objects.filter(groups__name="Delivery Crew")
        serialized_items = UserSerializer(crew, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        username = request.data['username']
        user = User.objects.get(username=username)
        
        group = Group.objects.get(name="Delivery Crew")
        group.user_set.add(user)
        return Response({"message": f"Delivery crew {username} is created"}, status=status.HTTP_201_CREATED)

@api_view(["GET", "DELETE"])
@permission_classes([IsManager | IsAdminUser])
def delivery_crew_member(request, pk):
    member = get_object_or_404(User, id=pk, groups__name="Delivery Crew")
    
    if request.method == "GET":
        serialized_item = UserSerializer(member)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    
    elif request.method == "DELETE":
        group = Group.objects.get(name="Delivery Crew")
        group.user_set.remove(member)
        return Response({"message": f"User {member.username} is deleted from Delivery crew group"}, status=status.HTTP_200_OK)

