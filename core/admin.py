from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from core.models import (
    FoodCategory, FoodItem, Order, OrderItem,
    OrderStatusHistory, CustomFoodRequest,
    Notification, Rating, TimeSlot
)
from chefs.models import (
    ChefProfile, ChefBankDetails, ChefDish,
    ChefEarnings, CuisineType, TodaysSpecial, FavouriteChef
)
from delivery.models import (
    DeliveryBoyProfile, DeliveryAssignment,
    DeliveryEarnings, DailyCashSummary
)
from customers.models import (
    CustomerProfile, Cart, CartItem,
    SavedAddress, MealSubscription
)


# ─── FOOD CATEGORY ───
@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display  = ['emoji', 'name', 'is_active']
    list_editable = ['is_active']


# ─── TIME SLOT ───
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time']


# ─── FOOD ITEM ───
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'selling_price',
                     'preparation_cost', 'profit_display',
                     'preparation_time', 'is_veg', 'is_available']
    list_filter   = ['category', 'is_veg', 'is_available']
    search_fields = ['name']
    list_editable = ['is_available']

    fieldsets = [
        ('Basic Info', {
            'fields': ['category', 'name', 'description',
                      'image', 'preparation_time',
                       'is_veg', 'serves', 'available_slots']
        }),
        ('Pricing - Visible to Everyone', {
            'fields': ['selling_price']
        }),
        ('🔒 ADMIN ONLY - Cost Details', {
            'fields': ['preparation_cost', 'ingredients'],
            'classes': ['collapse'],
            'description': '⚠️ Only visible to Admin. Never shown to customers or chefs.'
        }),
        ('Status', {
            'fields': ['is_available', 'is_todays_special']
        }),
    ]

    def profit_display(self, obj):
        profit = obj.selling_price - obj.preparation_cost
        color  = 'green' if profit > 0 else 'red'
        return format_html(
            '<span style="color:{}">₹{}</span>', color, profit
        )
    profit_display.short_description = '💰 Profit'


# ─── ORDER ITEM INLINE ───
class OrderItemInline(admin.TabularInline):
    model          = OrderItem
    extra          = 0
    readonly_fields = ['food_item', 'quantity', 'price']


# ─── ORDER ───
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'customer_name', 'chef_name',
                     'delivery_name', 'status_badge',
                     'payment_method', 'total_amount',
                     'chef_payment_released',
                     'delivery_payment_released', 'created_at']
    list_filter   = ['status', 'payment_method',
                     'chef_payment_released', 'created_at']
    search_fields = ['id']
    readonly_fields = ['created_at', 'accepted_at',
                       'ready_at', 'delivered_at', 'otp']
    inlines       = [OrderItemInline]
    actions       = ['release_daily_payments']

    def customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username
    customer_name.short_description = 'Customer'

    def chef_name(self, obj):
        return obj.chef.full_name if obj.chef else '—'
    chef_name.short_description = 'Chef'

    def delivery_name(self, obj):
        return obj.delivery_boy.full_name if obj.delivery_boy else '—'
    delivery_name.short_description = 'Delivery Boy'

    def status_badge(self, obj):
        colors = {
            'pending':   'orange',
            'accepted':  'blue',
            'preparing': 'purple',
            'ready':     'teal',
            'picked_up': 'navy',
            'on_way':    'indigo',
            'delivered': 'green',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background:{};color:white;'
            'padding:3px 8px;border-radius:4px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def release_daily_payments(self, request, queryset):
        released_chef     = 0
        released_delivery = 0

        for order in queryset.filter(status='delivered'):
            # Release chef payment
            if not order.chef_payment_released and order.chef:
                try:
                    earning = order.chef_earning
                    if not earning.is_paid:
                        earning.is_paid = True
                        earning.paid_at = timezone.now()
                        earning.save()
                        order.chef_payment_released = True
                        released_chef += 1
                except:
                    pass

            # Release delivery payment
            if not order.delivery_payment_released and order.delivery_boy:
                try:
                    earning = order.delivery_earning
                    if not earning.is_paid:
                        earning.is_paid = True
                        earning.paid_at = timezone.now()
                        earning.save()
                        order.delivery_payment_released = True
                        released_delivery += 1
                except:
                    pass

            order.save()

        self.message_user(
            request,
            f'✅ Payments released — '
            f'Chef: {released_chef} orders, '
            f'Delivery: {released_delivery} orders'
        )
    release_daily_payments.short_description = '💰 Release Daily Payments'


# ─── CHEF PROFILE ───
@admin.register(ChefProfile)
class ChefProfileAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'phone', 'city', 'state',
                     'is_approved', 'is_online', 'average_rating']
    list_editable = ['is_approved', 'is_online']
    list_filter   = ['is_approved', 'is_online', 'state']
    search_fields = ['user__first_name', 'user__last_name', 'phone']

    fieldsets = [
        ('Personal', {
            'fields': ['user', 'phone', 'gender',
                       'date_of_birth', 'profile_photo', 'bio']
        }),
        ('Address', {
            'fields': ['address', 'city', 'state',
                       'pincode', 'latitude', 'longitude']
        }),
        ('Food Details', {
            'fields': ['cuisine_types', 'is_vegetarian',
                       'is_non_vegetarian', 'is_vegan',
                       'experience_years', 'max_orders_per_slot',
                       'available_slots', 'available_days']
        }),
        ('Kitchen Photos', {
            'fields': ['kitchen_photo1', 'kitchen_photo2', 'kitchen_photo3']
        }),
        ('🔒 KYC - Admin Only', {
            'fields': ['aadhaar_number', 'pan_number'],
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ['is_approved', 'is_online', 'is_active']
        }),
    ]


# ─── CHEF DISH ───
@admin.register(ChefDish)
class ChefDishAdmin(admin.ModelAdmin):
    list_display = ['food_item', 'chef', 'price',
                    'preparation_cost', 'profit', 'is_available']
    list_filter  = ['is_available']

    def profit(self, obj):
        p     = obj.price - obj.preparation_cost
        color = 'green' if p > 0 else 'red'
        return format_html(
            '<span style="color:{}">₹{}</span>', color, p
        )
    profit.short_description = '💰 Profit'


# ─── CHEF EARNINGS ───
@admin.register(ChefEarnings)
class ChefEarningsAdmin(admin.ModelAdmin):
    list_display  = ['chef', 'order', 'amount', 'is_paid', 'paid_at', 'date']
    list_filter   = ['is_paid', 'date']
    list_editable = ['is_paid']
    actions       = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True, paid_at=timezone.now())
        self.message_user(
            request,
            f'✅ {queryset.count()} chef earnings marked as paid!'
        )
    mark_as_paid.short_description = '✅ Mark as Paid'


# ─── DELIVERY BOY PROFILE ───
@admin.register(DeliveryBoyProfile)
class DeliveryBoyProfileAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'phone', 'city',
                     'vehicle_type', 'is_approved', 'is_online']
    list_editable = ['is_approved', 'is_online']
    list_filter   = ['is_approved', 'is_online', 'vehicle_type']
    search_fields = ['user__first_name', 'user__last_name', 'phone']

    fieldsets = [
        ('Personal', {
            'fields': ['user', 'phone', 'profile_photo',
                       'address', 'city', 'pincode']
        }),
        ('🔒 Documents - Admin Only', {
            'fields': ['pan_number', 'licence_number'],
            'classes': ['collapse']
        }),
        ('Vehicle', {
            'fields': ['vehicle_type', 'vehicle_number']
        }),
        ('Bank Details', {
            'fields': ['account_holder', 'bank_name',
                       'account_number', 'ifsc_code', 'upi_id']
        }),
        ('Status', {
            'fields': ['is_approved', 'is_online', 'is_active']
        }),
    ]


# ─── DELIVERY EARNINGS ───
@admin.register(DeliveryEarnings)
class DeliveryEarningsAdmin(admin.ModelAdmin):
    list_display  = ['delivery_boy', 'order', 'amount',
                     'is_paid', 'paid_at', 'date']
    list_filter   = ['is_paid', 'date']
    list_editable = ['is_paid']
    actions       = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True, paid_at=timezone.now())
        self.message_user(
            request,
            f'✅ {queryset.count()} delivery earnings marked as paid!'
        )
    mark_as_paid.short_description = '✅ Mark as Paid'


# ─── DAILY CASH SUMMARY ───
@admin.register(DailyCashSummary)
class DailyCashSummaryAdmin(admin.ModelAdmin):
    list_display = ['delivery_boy', 'date', 'total_collected',
                    'total_submitted', 'pending_display', 'is_settled']
    list_filter  = ['is_settled', 'date']

    def pending_display(self, obj):
        pending = obj.pending_amount
        color   = 'red' if pending > 0 else 'green'
        return format_html(
            '<span style="color:{}">₹{}</span>', color, pending
        )
    pending_display.short_description = 'Pending'


# ─── CUSTOMER PROFILE ───
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'phone', 'home_state', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'phone']


# ─── REGISTER REMAINING MODELS ───
admin.site.register(CuisineType)
admin.site.register(ChefBankDetails)
admin.site.register(TodaysSpecial)
admin.site.register(FavouriteChef)
admin.site.register(DeliveryAssignment)
admin.site.register(CustomFoodRequest)
admin.site.register(Rating)
admin.site.register(Notification)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(SavedAddress)
admin.site.register(MealSubscription)