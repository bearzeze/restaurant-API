from django.urls import path, include
from . import classBasedViews, functionBasedViews

app_name = "LittleLemonAPI"

urlpatterns = [
    
    # CLASS-BASED VIEWS - they are in views.py file
    # path('categories/', classBasedViews.CategoryView.as_view()),
    # path('categories/<int:pk>', classBasedViews.SingleCategoryView.as_view()),
    
    # path('menu-items/', classBasedViews.MenuItemsView.as_view()),
    # path('menu-items/<int:pk>', classBasedViews.SingleMenuItemView.as_view()),

    
    # FUNCTION-BASED VIEWS - they are in helpers.py file
    path('categories/', functionBasedViews.categories),
    path('categories/<int:pk>', functionBasedViews.category),
    
    path('menu-items/', functionBasedViews.menu_items),
    path('menu-items/<int:pk>', functionBasedViews.single_menu_item),
    
    path('cart/menu-items', functionBasedViews.cart),
    
    path('orders/', functionBasedViews.orders),
    path('orders/<int:pk>', functionBasedViews.order),
    
    path('users', functionBasedViews.user_registration),
    path('users/', include('djoser.urls')),

    path("groups/manager/users/", functionBasedViews.managers, name="managers"),
    path("groups/manager/users/<int:pk>", functionBasedViews.manager, name="manager"),
    
    path("groups/delivery_crew/users/", functionBasedViews.delivery_crew, name="delivery_crew"),
    path("groups/delivery_crew/users/<int:pk>", functionBasedViews.delivery_crew_member, name="delivery_crew_member"),

]