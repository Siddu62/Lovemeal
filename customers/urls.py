from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path('register/', views.customer_register, name='register'),
    path('login/', views.customer_login, name='login'),
    path('logout/', views.customer_logout, name='logout'),
 
    # path('register/', views.customer_register, name='register'),
    # path('login/', views.customer_login, name='login'),
    # path('logout/', views.customer_logout, name='logout'),

    # CART
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order")
]