from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import ChefProfile
from django.contrib.auth.decorators import login_required
from core.models import Order
from chefs.models import ChefEarnings
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
# ---------------- CHEF LOGIN ----------------
def chef_login(request):
    # if request.user.is_authenticated:
    #     return redirect('/chefs/dashboard/')
        # return redirect('chefs:dashboard')
    if request.user.is_authenticated and hasattr(request.user, "chef_profile"):
        return redirect('chefs:dashboard')
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user and hasattr(user, "chef_profile"):
            login(request, user)
            return redirect('/chefs/dashboard/')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "chefs/login.html")

# ---------------- CHEF LOGOUT ----------------
def chef_logout(request):
    logout(request)
    # return redirect('/')
    return redirect('core:homepage')

# ---------------- ACCEPT ORDER ----------------
@login_required
def accept_order(request, order_id):
    chef = request.user.chef_profile
    order = get_object_or_404(Order, id=order_id)
    if order.chef is None:
        order.chef = chef
        order.status = "accepted"
        order.accepted_at = timezone.now()
        order.save()
    return redirect('chefs:dashboard')

# ---------------- START COOKING ----------------
@login_required
def start_cooking(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status == "accepted":
        order.status = "preparing"
        order.save()
    return redirect('chefs:dashboard')

# ---------------- MARK READY ----------------
# @login_required
# def mark_ready(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     if order.status == "preparing":
#         order.status = "ready"
#         order.ready_at = timezone.now()
#         order.save()
#     return redirect('chefs:dashboard')
# ---------------- MARK READY ----------------
@login_required
def mark_ready(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # FIX: Check for "accepted" (or "preparing") so the button actually works!
    if order.status in ["accepted", "preparing"]:
        order.status = "ready"
        order.ready_at = timezone.now()
        order.save()
    return redirect('chefs:dashboard')
# ---------------- CHEF REGISTER ----------------
def chef_register(request):
    # if request.user.is_authenticated:
    #     return redirect('/')
    # if request.user.is_authenticated:
    #     return redirect('chefs:dashboard')
    if request.user.is_authenticated and hasattr(request.user, "chef_profile"):
        return redirect('chefs:dashboard')
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")
        # validations
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists")
            return redirect("chefs:register")
        if ChefProfile.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered")
            return redirect("chefs:register")
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("chefs:register")
        # create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        # create chef profile automatically
        ChefProfile.objects.create(
            user=user,
            phone=phone,
            address="",
            city="",
            state="",
            pincode=""
        )
        login(request, user)
        messages.success(request, "Chef account created successfully! Please login.")
        return redirect("chefs:login")
    return render(request, "chefs/register.html")

from django.db.models import Sum
@login_required
def chef_dashboard(request):
    if not hasattr(request.user, "chef_profile"):
        return redirect("core:homepage")
    chef = request.user.chef_profile
    # Incoming orders (not accepted yet)
    incoming_orders = Order.objects.filter(
        status="pending"
    )
    # Accepted orders -> show in Preparing table
    preparing_orders = Order.objects.filter(
        chef=chef,
        status="accepted"
    )
    # Cooking finished -> show Ready table
    ready_orders = Order.objects.filter(
        chef=chef,
        status="ready"
    )
    # Delivered -> Completed orders
    completed_orders = Order.objects.filter(
        chef=chef,
        status="delivered"
    )
    # total_earnings = completed_orders.aggregate(
    #     total=Sum("chef_earning")
    # )["total"] or 0
    # ✅ FIX: We must specify "__amount" so Django knows which column to sum up!
    total_earnings = completed_orders.aggregate(
        total=Sum("chef_earning__amount")
    )["total"] or 0
    return render(request,"chefs/dashboard.html",{
        "chef": chef,
        "incoming_orders": incoming_orders,
        "preparing_orders": preparing_orders,
        "ready_orders": ready_orders,
        "completed_orders": completed_orders,
        "completed_orders_count": completed_orders.count(),
        "total_earnings": total_earnings
    })
# from django.db.models import Sum

# @login_required
# def chef_dashboard(request):

#     if not hasattr(request.user, "chef_profile"):
#         return redirect("core:homepage")

#     chef = request.user.chef_profile

#     # Orders waiting for chef
#     incoming_orders = Order.objects.filter(
#         status="pending"
#     )

#     # Orders currently cooking
#     preparing_orders = Order.objects.filter(
#         chef=chef,
#         status="preparing"
#     )

#     # Orders ready for delivery
#     ready_orders = Order.objects.filter(
#         chef=chef,
#         status="ready"
#     )

#     # Completed orders
#     completed_orders = Order.objects.filter(
#         chef=chef,
#         status="delivered"
#     )

#     completed_count = completed_orders.count()

#     total_earnings = completed_orders.aggregate(
#         total=Sum("chef_earning")
#     )["total"] or 0

#     return render(request, "chefs/dashboard.html", {
#         "incoming_orders": incoming_orders,
#         "preparing_orders": preparing_orders,
#         "ready_orders": ready_orders,
#         "completed_orders": completed_orders,
#         "completed_orders_count": completed_count,
#         "total_earnings": total_earnings
#     })




# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.utils import timezone
# from django.db.models import Sum

# from chefs.models import ChefProfile, ChefBankDetails
# from core.models import Order, Notification, TimeSlot


# # ─── REGISTRATION ───
# def chef_register(request):
#     if request.user.is_authenticated and hasattr(request.user, 'chef_profile'):
#         return redirect('chefs:dashboard')

#     if request.method == 'POST':
#         # Get form data
#         first_name = request.POST.get('first_name', '').strip()
#         last_name  = request.POST.get('last_name', '').strip()
#         email      = request.POST.get('email', '').strip()
#         phone      = request.POST.get('phone', '').strip()
#         password   = request.POST.get('password', '')

#         # Validations
#         if User.objects.filter(email=email).exists():
#             messages.error(request, 'Email already registered.')
#             return render(request, 'chefs/register.html')

#         if ChefProfile.objects.filter(phone=phone).exists():
#             messages.error(request, 'Phone number already registered.')
#             return render(request, 'chefs/register.html')

#         # Create user
#         user = User.objects.create_user(
#             username   = email,
#             email      = email,
#             password   = password,
#             first_name = first_name,
#             last_name  = last_name,
#         )

#         # Create chef profile
#         chef = ChefProfile.objects.create(
#             user       = user,
#             phone      = phone,
#             gender     = request.POST.get('gender', 'M'),
#             address    = request.POST.get('address', ''),
#             city       = request.POST.get('city', ''),
#             state      = request.POST.get('state', ''),
#             pincode    = request.POST.get('pincode', ''),
#             bio        = request.POST.get('bio', ''),
#             is_vegetarian = request.POST.get('is_vegetarian') == 'on',
#             is_non_vegetarian = request.POST.get('is_non_vegetarian') == 'on',
#         )

#         # Create bank details
#         ChefBankDetails.objects.create(
#             chef           = chef,
#             account_holder = request.POST.get('account_holder', ''),
#             bank_name      = request.POST.get('bank_name', ''),
#             account_number = request.POST.get('account_number', ''),
#             ifsc_code      = request.POST.get('ifsc_code', ''),
#             upi_id         = request.POST.get('upi_id', ''),
#         )

#         # Auto login
#         login(request, user)
#         messages.success(request, 'Registration successful! Please wait for admin approval.')
#         return redirect('chefs:dashboard')

#     return render(request, 'chefs/register.html')


# # ─── LOGIN ───
# def chef_login(request):
#     if request.user.is_authenticated and hasattr(request.user, 'chef_profile'):
#         return redirect('chefs:dashboard')

#     if request.method == 'POST':
#         email    = request.POST.get('email', '').strip()
#         password = request.POST.get('password', '')
#         user     = authenticate(request, username=email, password=password)

#         if user and hasattr(user, 'chef_profile'):
#             login(request, user)
#             messages.success(request, f'Welcome back, {user.first_name}!')
#             return redirect('chefs:dashboard')
#         else:
#             messages.error(request, 'Invalid credentials or not a chef account.')

#     return render(request, 'chefs/login.html')


# # ─── DASHBOARD ───
# @login_required
# def chef_dashboard(request):
#     try:
#         chef = request.user.chef_profile
#     except:
#         messages.error(request, 'You need to register as a chef first!')
#         return redirect('chefs:register')

#     if not chef.is_approved:
#         return render(request, 'chefs/not_approved.html', {'chef': chef})

#     # Incoming Orders - Waiting for chef to accept
#     incoming_orders = Order.objects.filter(
#         status='pending'
#     ).select_related('customer').prefetch_related('items__food_item').order_by('-created_at')

#     # Preparing Orders - Chef accepted, now preparing
#     preparing_orders = Order.objects.filter(
#         chef=chef,
#         status__in=['accepted', 'preparing']
#     ).select_related('customer').prefetch_related('items__food_item').order_by('-accepted_at')

#     # Ready Orders - Food is ready, waiting for delivery
#     ready_orders = Order.objects.filter(
#         chef=chef,
#         status='ready',
#         delivery_boy__isnull=True
#     ).select_related('customer').prefetch_related('items__food_item').order_by('-ready_at')

#     # Completed Orders
#     completed_orders = Order.objects.filter(
#         chef=chef,
#         status='delivered'
#     ).select_related('customer').prefetch_related('items__food_item').order_by('-delivered_at')[:10]

#     # Today's earnings
#     today = timezone.now().date()
#     from chefs.models import ChefEarnings
#     today_earnings = ChefEarnings.objects.filter(
#         chef=chef,
#         date=today
#     ).aggregate(total=Sum('amount'))['total'] or 0

#     # Total completed orders count
#     total_completed = Order.objects.filter(chef=chef, status='delivered').count()

#     context = {
#         'chef': chef,
#         'incoming_orders': incoming_orders,
#         'preparing_orders': preparing_orders,
#         'ready_orders': ready_orders,
#         'completed_orders': completed_orders,
#         'today_earnings': today_earnings,
#         'total_completed': total_completed,
#     }
#     return render(request, 'chefs/dashboard.html', context)


# # ─── CHEF ACTIONS ───
# @login_required
# @require_POST
# def chef_accept_order(request, order_id):
#     try:
#         chef = request.user.chef_profile
#     except:
#         return JsonResponse({'success': False, 'message': 'Chef profile not found'})

#     try:
#         order = Order.objects.select_for_update().get(id=order_id, status='pending')
        
#         # Assign chef and update status
#         order.chef = chef
#         order.status = 'accepted'
#         order.accepted_at = timezone.now()
#         order.save()

#         # Notify customer
#         Notification.objects.create(
#             user=order.customer,
#             type='order_accepted',
#             title='Order Accepted!',
#             message=f'Chef {chef.full_name} has accepted your order #{order.id}',
#             order=order,
#         )

#         messages.success(request, f'Order #{order.id} accepted! Start preparing.')
#         return JsonResponse({'success': True, 'message': 'Order accepted!'})

#     except Order.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Order already taken by another chef!'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)})


# @login_required
# @require_POST
# def chef_start_preparing(request, order_id):
#     try:
#         chef = request.user.chef_profile
#         order = get_object_or_404(Order, id=order_id, chef=chef, status='accepted')

#         order.status = 'preparing'
#         order.save()

#         # Notify customer
#         Notification.objects.create(
#             user=order.customer,
#             type='order_accepted',
#             title='Food is Being Prepared!',
#             message=f'Chef {chef.full_name} is now preparing your order #{order.id}',
#             order=order,
#         )

#         messages.success(request, f'Order #{order.id} moved to preparing!')
#         return JsonResponse({'success': True})

#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)})


# @login_required
# @require_POST
# def chef_mark_ready(request, order_id):
#     try:
#         chef = request.user.chef_profile
#         order = get_object_or_404(Order, id=order_id, chef=chef, status='preparing')

#         order.status = 'ready'
#         order.ready_at = timezone.now()
#         order.save()

#         # Notify customer
#         Notification.objects.create(
#             user=order.customer,
#             type='food_ready',
#             title='Food is Ready!',
#             message=f'Your order #{order.id} is ready and waiting for delivery pickup',
#             order=order,
#         )

#         messages.success(request, f'Order #{order.id} marked as ready! Delivery boys will be notified.')
#         return JsonResponse({'success': True})

#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)})


# # ─── LOGOUT ───
# @login_required
# def chef_logout(request):
#     logout(request)
#     messages.success(request, 'Logged out successfully!')
#     return redirect('/')