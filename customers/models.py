from django.db import models
from django.contrib.auth.models import User
from core.models import FoodItem


# ─── CUSTOMER PROFILE ───
class CustomerProfile(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone         = models.CharField(max_length=15, unique=True)
    profile_photo = models.URLField(blank=True)
    home_state    = models.CharField(max_length=100, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer: {self.user.get_full_name() or self.user.username}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


# ─── SAVED ADDRESS ───
class SavedAddress(models.Model):
    customer   = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='addresses')
    label      = models.CharField(max_length=50)
    address    = models.TextField()
    city       = models.CharField(max_length=100)
    pincode    = models.CharField(max_length=10)
    latitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.full_name} - {self.label}"


# ─── CART ───
class Cart(models.Model):
    customer   = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.customer.full_name}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.cart_items.all())

    @property
    def item_count(self):
        return self.cart_items.count()


# ─── CART ITEM ───
class CartItem(models.Model):
    cart      = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"

    @property
    def subtotal(self):
        return self.food_item.selling_price * self.quantity


# ─── MEAL SUBSCRIPTION ───
class MealSubscription(models.Model):
    PLAN_CHOICES = [
        ('weekly',  'Weekly  (5 Days)'),
        ('monthly', 'Monthly (22 Days)'),
    ]
    STATUS_CHOICES = [
        ('active',    'Active'),
        ('paused',    'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch',     'Lunch'),
        ('dinner',    'Dinner'),
    ]

    customer     = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='subscriptions')
    chef         = models.ForeignKey('chefs.ChefProfile', on_delete=models.CASCADE, related_name='subscriptions')
    food_item    = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    plan         = models.CharField(max_length=10, choices=PLAN_CHOICES)
    meal_type    = models.CharField(max_length=10, choices=MEAL_CHOICES)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    start_date   = models.DateField()
    end_date     = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.full_name} - {self.plan} {self.meal_type}"