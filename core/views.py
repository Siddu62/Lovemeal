from django.shortcuts import render
from core.models import FoodItem

def homepage(request):
    foods = FoodItem.objects.filter(is_available=True)

    return render(request, "core/homepage.html", {
        "foods": foods
    })
# def restaurant_food(request):
#     foods = FoodItem.objects.filter(is_available=True)
#     return render(request, "core/restaurant_food.html", {
#         "foods": foods
#     })
def restaurant_food(request):
    foods = FoodItem.objects.filter(is_available=True)

    category = request.GET.get("category")
    if category:
        foods = foods.filter(category__name=category)

    query = request.GET.get("q")
    if query:
        foods = foods.filter(name__icontains=query)

    return render(request, "core/restaurant_food.html", {
        "foods": foods
    })

def home_food(request):
    foods = FoodItem.objects.filter(is_available=True)
    return render(request, "core/home_food.html", {
        "foods": foods
    })

def popular_food(request):
    foods = FoodItem.objects.filter(is_available=True, is_todays_special=True)
    return render(request, "core/popular_food.html", {
        "foods": foods
    })



