from django.urls import path
from . import views
app_name = 'core'

urlpatterns = [
    path('', views.homepage, name='homepage'),

    path('restaurant-food/', views.restaurant_food, name='restaurant_food'),
    path('home-food/', views.home_food, name='home_food'),
    path('popular-food/', views.popular_food, name='popular_food'),
]