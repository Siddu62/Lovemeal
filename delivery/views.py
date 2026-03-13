from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from urllib3 import request
from core.models import Order
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from delivery.models import DeliveryBoyProfile, DeliveryEarnings
from chefs.models import ChefEarnings
import random
# ---------------- DELIVERY REGISTER ----------------
def delivery_register(request):
    if request.user.is_authenticated and hasattr(request.user, "delivery_profile"):
        return redirect("delivery:dashboard")
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect("delivery:register")
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name
        )
        DeliveryBoyProfile.objects.create(
            user=user,
            phone=phone
        )
        messages.success(request, "Account created successfully. Please login.")
        return redirect("delivery:login")
    return render(request, "delivery/register.html")
# ---------------- DELIVERY LOGIN ----------------
def delivery_login(request):
    if request.user.is_authenticated and hasattr(request.user, "delivery_profile"):
        return redirect("delivery:dashboard")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            if not hasattr(user, "delivery_profile"):
                messages.error(request, "This account is not a delivery account")
                return redirect("delivery:login")
            login(request, user)
            return redirect("delivery:dashboard")
        else:
            messages.error(request, "Invalid email or password")
    return render(request, "delivery/login.html")

# ---------------- DELIVERY LOGOUT ----------------
def delivery_logout(request):
    logout(request)
    return redirect("core:homepage")

# ---------------- DELIVERY DASHBOARD ----------------
# from django.db.models import Sum
# @login_required
# def delivery_dashboard(request):
#     if not hasattr(request.user, "delivery_profile"):
#         return redirect("core:homepage")
#     delivery_boy = request.user.delivery_profile
#     # Orders waiting for delivery boy
#     ready_orders = Order.objects.filter(
#         status="ready",
#         delivery_boy__isnull=True
#     )
#     # Orders currently being delivered
#     delivering_orders = Order.objects.filter(
#         delivery_boy=delivery_boy,
#         status="picked_up"
#     )
#     # Completed deliveries
#     completed_orders = Order.objects.filter(
#         delivery_boy=delivery_boy,
#         status="delivered"
#     )
#     # Calculate delivery earnings
#     total_earnings = completed_orders.aggregate(
#         total=Sum("delivery_earning")
#     )["total"] or 0
#     return render(request, "delivery/dashboard.html", {
#         "ready_orders": ready_orders,
#         "delivering_orders": delivering_orders,
#         "completed_orders": completed_orders,
#         "completed_count": completed_orders.count(),
#         "total_earnings": total_earnings
#     })


@login_required
def delivery_dashboard(request):
    # ✅ Add this safety check to prevent the crash!
    if not hasattr(request.user, "delivery_profile"):
        return redirect("core:homepage")
    delivery_boy = request.user.delivery_profile
    ready_orders = Order.objects.filter(
        status="ready",
        delivery_boy__isnull=True
    )
    # ✅ FIX: Match the template name "delivering_orders" and look for "picked_up"
    delivering_orders = Order.objects.filter(
        delivery_boy=delivery_boy,
        status="picked_up"
    )

    # accepted_orders = Order.objects.filter(
    #     delivery_boy=delivery_boy,
    #     status="picked_up"
    # )
    # travelling_orders = Order.objects.filter(
    #     delivery_boy=delivery_boy,
    #     status="travelling"
    # )

    completed_orders = Order.objects.filter(
        delivery_boy=delivery_boy,
        status="delivered"
    )
    # total_earnings = completed_orders.aggregate(
    #     total=Sum("delivery_earning")
    # )["total"] or 0
    # ✅ FIX: Calculate total using "delivery_earning__amount"
    total_earnings = completed_orders.aggregate(
        total=Sum("delivery_earning__amount")
    )["total"] or 0
    return render(request,"delivery/dashboard.html",{
        "ready_orders": ready_orders,
        # "accepted_orders": accepted_orders,
        # "travelling_orders": travelling_orders,
        "delivering_orders": delivering_orders,  # Passed to template here!
        "completed_orders": completed_orders,
        "completed_count": completed_orders.count(),
        "total_earnings": total_earnings
    })
# ---------------- PICKUP ORDER ----------------
@login_required
def pickup_order(request, order_id):
    delivery_boy = request.user.delivery_profile
    order = get_object_or_404(Order, id=order_id)

    if order.delivery_boy is None:
        order.delivery_boy = delivery_boy
        order.status = "picked_up"
        order.save()
    return redirect("delivery:dashboard")

# ---------------- MARK DELIVERED & ADD EARNINGS ----------------
@login_required
def deliver_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Check so we don't accidentally create earnings twice
    if order.status != "delivered":
        order.status = "delivered"
        order.save()
        # ✅ GENERATE RANDOM EARNINGS
        delivery_fee = random.randint(15, 25)
        chef_profit = random.randint(25, 40)
        # ✅ SAVE DELIVERY EARNING TO DATABASE
        DeliveryEarnings.objects.get_or_create(
            delivery_boy=order.delivery_boy,
            order=order,
            defaults={'amount': delivery_fee}
        )
        # ✅ SAVE CHEF EARNING TO DATABASE
        if order.chef:
            ChefEarnings.objects.get_or_create(
                chef=order.chef,
                order=order,
                defaults={'amount': chef_profit}
            )
    return redirect("delivery:dashboard")

# # ---------------- START TRAVELLING ----------------
# @login_required
# def start_delivery(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     order.status = "travelling"
#     order.save()
#     return redirect("delivery:dashboard")
# # ---------------- MARK DELIVERED ----------------
# @login_required
# def deliver_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     order.status = "delivered"
#     order.save()
#     return redirect("delivery:dashboard")




# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.utils import timezone
# from django.db.models import Sum

# from delivery.models import DeliveryBoyProfile, DeliveryAssignment, DeliveryEarnings
# from core.models import Order, Notification


# # ─── REGISTRATION ───
# def delivery_register(request):
#     if request.user.is_authenticated and hasattr(request.user, 'delivery_profile'):
#         return redirect('delivery:dashboard')

#     if request.method == 'POST':
#         first_name = request.POST.get('first_name', '').strip()
#         last_name  = request.POST.get('last_name', '').strip()
#         email      = request.POST.get('email', '').strip()
#         phone      = request.POST.get('phone', '').strip()
#         password   = request.POST.get('password', '')

#         if User.objects.filter(email=email).exists():
#             messages.error(request, 'Email already registered.')
#             return render(request, 'delivery/register.html')

#         user = User.objects.create_user(
#             username   = email,
#             email      = email,
#             password   = password,
#             first_name = first_name,
#             last_name  = last_name,
#         )

#         DeliveryBoyProfile.objects.create(
#             user           = user,
#             phone          = phone,
#             address        = request.POST.get('address', ''),
#             city           = request.POST.get('city', ''),
#             pincode        = request.POST.get('pincode', ''),
#             vehicle_type   = request.POST.get('vehicle_type', 'bike'),
#             vehicle_number = request.POST.get('vehicle_number', ''),
#             account_holder = request.POST.get('account_holder', ''),
#             bank_name      = request.POST.get('bank_name', ''),
#             account_number = request.POST.get('account_number', ''),
#             ifsc_code      = request.POST.get('ifsc_code', ''),
#         )

#         login(request, user)
#         messages.success(request, 'Registration successful! Please wait for admin approval.')
#         return redirect('delivery:dashboard')

#     return render(request, 'delivery/register.html')


# # ─── LOGIN ───
# def delivery_login(request):
#     if request.user.is_authenticated and hasattr(request.user, 'delivery_profile'):
#         return redirect('delivery:dashboard')

#     if request.method == 'POST':
#         email    = request.POST.get('email', '').strip()
#         password = request.POST.get('password', '')
#         user     = authenticate(request, username=email, password=password)

#         if user and hasattr(user, 'delivery_profile'):
#             login(request, user)
#             messages.success(request, f'Welcome back, {user.first_name}!')
#             return redirect('delivery:dashboard')
#         else:
#             messages.error(request, 'Invalid credentials or not a delivery account.')

#     return render(request, 'delivery/login.html')


# # ─── DASHBOARD ───
# @login_required
# def delivery_dashboard(request):
#     try:
#         delivery = request.user.delivery_profile
#     except:
#         messages.error(request, 'You need to register as a delivery partner first!')
#         return redirect('delivery:register')

#     if not delivery.is_approved:
#         return render(request, 'delivery/not_approved.html', {'delivery': delivery})

#     # Ready Orders - Food is ready, waiting for delivery pickup
#     ready_orders = Order.objects.filter(
#         status='ready'
#     ).select_related('customer', 'chef').prefetch_related('items__food_item').order_by('-ready_at')

#     # Travelling Orders - Delivery boy accepted and travelling
#     travelling_orders = DeliveryAssignment.objects.filter(
#         delivery_boy=delivery,
#         status__in=['assigned', 'picked_up', 'on_way']
#     ).select_related('order__customer', 'order__chef').prefetch_related('order__items__food_item').order_by('-assigned_at')

#     # Completed Deliveries
#     completed_deliveries = DeliveryAssignment.objects.filter(
#         delivery_boy=delivery,
#         status='delivered'
#     ).select_related('order__customer').prefetch_related('order__items__food_item').order_by('-delivered_at')[:10]

#     # Today's earnings
#     today = timezone.now().date()
#     today_earnings = DeliveryEarnings.objects.filter(
#         delivery_boy=delivery,
#         date=today
#     ).aggregate(total=Sum('amount'))['total'] or 0

#     # Total completed count
#     total_completed = DeliveryAssignment.objects.filter(
#         delivery_boy=delivery,
#         status='delivered'
#     ).count()

#     context = {
#         'delivery': delivery,
#         'ready_orders': ready_orders,
#         'travelling_orders': travelling_orders,
#         'completed_deliveries': completed_deliveries,
#         'today_earnings': today_earnings,
#         'total_completed': total_completed,
#     }
#     return render(request, 'delivery/dashboard.html', context)


# # ─── DELIVERY ACTIONS ───
# @login_required
# @require_POST
# def delivery_accept_order(request, order_id):
#     try:
#         delivery = request.user.delivery_profile
#         order = Order.objects.select_for_update().get(id=order_id, status='ready')

#         # Assign delivery boy
#         order.delivery_boy = delivery
#         order.status = 'picked_up'
#         order.picked_up_at = timezone.now()
#         order.save()

#         # Create delivery assignment
#         assignment = DeliveryAssignment.objects.create(
#             delivery_boy=delivery,
#             order=order,
#             status='assigned',
#             pickup_address=f"{order.chef.address}, {order.chef.city}",
#             pickup_lat=order.chef.latitude,
#             pickup_lng=order.chef.longitude,
#             drop_address=order.delivery_address,
#             drop_lat=order.delivery_lat,
#             drop_lng=order.delivery_lng,
#             cod_amount=order.total_amount if order.payment_method == 'cod' else 0,
#         )

#         # Notify customer
#         Notification.objects.create(
#             user=order.customer,
#             type='out_for_delivery',
#             title='Out for Delivery!',
#             message=f'Your order #{order.id} is being delivered by {delivery.full_name}',
#             order=order,
#         )

#         messages.success(request, f'Order #{order.id} accepted for delivery!')
#         return JsonResponse({'success': True})

#     except Order.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Order already taken by another delivery partner!'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)})


# @login_required
# @require_POST
# def delivery_mark_destination(request, assignment_id):
#     try:
#         delivery = request.user.delivery_profile
#         assignment = get_object_or_404(DeliveryAssignment, id=assignment_id, delivery_boy=delivery)

#         # Update to on_way status
#         assignment.status = 'on_way'
#         assignment.save()

#         assignment.order.status = 'on_way'
#         assignment.order.save()

#         # Notify customer
#         Notification.objects.create(
#             user=assignment.order.customer,
#             type='out_for_delivery',
#             title='Almost There!',
#             message=f'Your order #{assignment.order.id} will arrive soon!',
#             order=assignment.order,
#         )

#         messages.success(request, f'On the way to customer!')
#         return JsonResponse({'success': True})

#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)})


# @login_required
# @require_POST
# def delivery_mark_delivered(request, assignment_id):
#     try:
#         delivery = request.user.delivery_profile
#         assignment = get_object_or_404(DeliveryAssignment, id=assignment_id, delivery_boy=delivery)

#         # Mark as delivered
#         assignment.status = 'delivered'
#         assignment.delivered_at = timezone.now()
#         assignment.save()

#         assignment.order.status = 'delivered'
#         assignment.order.delivered_at = timezone.now()
#         assignment.order.save()

#         # Create earnings records
#         from chefs.models import ChefEarnings
#         from django.conf import settings

#         # Chef earning
#         commission = (assignment.order.total_amount * settings.PLATFORM_COMMISSION_PERCENT) / 100
#         chef_amount = assignment.order.total_amount - commission - settings.DELIVERY_BOY_FEE

#         ChefEarnings.objects.create(
#             chef=assignment.order.chef,
#             order=assignment.order,
#             amount=chef_amount,
#         )

#         # Delivery earning
#         DeliveryEarnings.objects.create(
#             delivery_boy=delivery,
#             order=assignment.order,
#             amount=settings.DELIVERY_BOY_FEE,
#         )

#         # Notify customer
#         Notification.objects.create(
#             user=assignment.order.customer,
#             type='delivered',
#             title='Order Delivered!',
#             message=f'Your order #{assignment.order.id} has been delivered. Enjoy your meal! 🍱',
#             order=assignment.order,
#         )

#         messages.success(request, f'Order #{assignment.order.id} delivered successfully!')
#         return JsonResponse({'success': True})

#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)})


# # ─── LOGOUT ───
# @login_required
# def delivery_logout(request):
#     logout(request)
#     messages.success(request, 'Logged out successfully!')
#     return redirect('/')