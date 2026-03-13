from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from customers.models import CustomerProfile, Cart
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from core.models import FoodItem, Order, OrderItem
from customers.models import CartItem


def customer_register(request):
    # if request.user.is_authenticated:
    #     return redirect('/')
    # if request.user.is_authenticated:
    #     return redirect('customers:dashboard')
    if request.user.is_authenticated and hasattr(request.user, "customer_profile"):
        return redirect('customers:dashboard')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        password   = request.POST.get('password', '')
        confirm_pw = request.POST.get('confirm_password', '')
        home_state = request.POST.get('home_state', '').strip()
        # Validations
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login.')
            return render(request, 'customers/register.html')
        if CustomerProfile.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered.')
            return render(request, 'customers/register.html')
        if password != confirm_pw:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'customers/register.html')
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'customers/register.html')
        # Create user
        user = User.objects.create_user(
            username   = email,
            email      = email,
            password   = password,
            first_name = first_name,
            last_name  = last_name,
        )
        # Create customer profile
        customer = CustomerProfile.objects.create(
            user       = user,
            phone      = phone,
            home_state = home_state,
        )
        # Create empty cart
        Cart.objects.create(customer=customer)
        # Auto login
        login(request, user)
        messages.success(request, f'Welcome to Lovemeal, {first_name}! 🍱')
        # return redirect('/')
        # messages.success(request, "Account created successfully. Please login.")
        return redirect('customers:login')
    return render(request, 'customers/register.html')

def customer_login(request):
    # if request.user.is_authenticated:
    #     return redirect('/')
    # if request.user.is_authenticated:
    #     return redirect('customers:dashboard')
    if request.user.is_authenticated and hasattr(request.user, "customer_profile"):
        return redirect('customers:dashboard')
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            # Check it's a customer
            if not hasattr(user, 'customer_profile'):
                messages.error(request, 'This account is not a customer account.')
                return render(request, 'customers/login.html')
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}! 🍱')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'customers/login.html')

def customer_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('/')
# ---------------- CART ----------------
@login_required
def add_to_cart(request, food_id):
    if not hasattr(request.user, "customer_profile"):
        messages.error(request, "Please login as customer to order food.")
        return redirect("customers:login")
    food = FoodItem.objects.get(id=food_id)
    customer = request.user.customer_profile
    cart = customer.cart
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        food_item=food
    )
    if not created:
        item.quantity += 1
        item.save()
    return redirect('customers:cart')

@login_required
def view_cart(request):
    if not hasattr(request.user, "customer_profile"):
        return redirect("customers:login")
    cart = request.user.customer_profile.cart
    items = cart.cart_items.all()
    return render(request, 'customers/cart.html', {
        'cart': cart,
        'items': items
    })

@login_required
def place_order(request):
    if not hasattr(request.user, "customer_profile"):
        return redirect("customers:login")
    customer = request.user.customer_profile
    cart = customer.cart
    items = cart.cart_items.all()
    if not items:
        return redirect('customers:cart')
    order = Order.objects.create(
        customer=request.user,
        total_amount=cart.total,
        # delivery_address="Default Address",
        delivery_address=customer.home_state or "Not Provided",
        contact_number=customer.phone,
        otp=get_random_string(6, allowed_chars='0123456789')
    )
    for item in items:
        OrderItem.objects.create(
            order=order,
            food_item=item.food_item,
            quantity=item.quantity,
            price=item.food_item.selling_price
        )
    items.delete()
    return redirect('/')

from django.db.models import Sum
@login_required
def customer_dashboard(request):
    orders = request.user.orders.prefetch_related("items")
    total_orders = orders.count()
    total_spent = orders.aggregate(
        total=Sum("total_amount")
    )["total"] or 0
    return render(request, "customers/dashboard.html", {
        "orders": orders,
        "total_orders": total_orders,
        "total_spent": total_spent
    })

from django.shortcuts import get_object_or_404
@login_required
def mark_received(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.customer == request.user:
        order.status = "received"
        order.save()
    return redirect("customers:dashboard")

# from django.shortcuts import get_object_or_404
# @login_required
# def cancel_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id, customer=request.user)
#     if order.status == "pending":
#         order.status = "cancelled"
#         order.save()
#     return redirect("customers:dashboard")

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user   # ✅ VERY IMPORTANT FIX
    )
    if order.status == "pending":
        order.delete()
    return redirect("customers:dashboard")