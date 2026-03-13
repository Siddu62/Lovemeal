from django.urls import path
from . import views
app_name = 'chefs'
urlpatterns = [
    path('register/', views.chef_register, name='register'),
    path('login/',    views.chef_login,    name='login'),
    path('logout/',   views.chef_logout,   name='logout'),
    path('dashboard/', views.chef_dashboard, name='dashboard'),
    path('accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('start-cooking/<int:order_id>/', views.start_cooking, name='start_cooking'),
    path('mark-ready/<int:order_id>/', views.mark_ready, name='mark_ready')
]
