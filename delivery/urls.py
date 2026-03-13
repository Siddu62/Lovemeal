from django.urls import path
from . import views
app_name = 'delivery'
urlpatterns = [
    path('register/', views.delivery_register, name='register'),
    path('login/',    views.delivery_login,    name='login'),
    path('logout/',   views.delivery_logout,   name='logout'),
    path('dashboard/', views.delivery_dashboard, name='dashboard'),
    path('pickup/<int:order_id>/', views.pickup_order, name='pickup_order'),
    path('deliver/<int:order_id>/', views.deliver_order, name='deliver_order'),
]
