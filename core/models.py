from django.db import models
from django.contrib.auth.models import User


# ─── FOOD CATEGORY ───
class FoodCategory(models.Model):
    name       = models.CharField(max_length=100)
    emoji      = models.CharField(max_length=10, default='🍽️')
    image_url  = models.URLField(blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Food Categories"
        ordering = ['name']

    def __str__(self):
        return f"{self.emoji} {self.name}"


# ─── TIME SLOT ───
class TimeSlot(models.Model):
    SLOT_CHOICES = [
        ('morning',   'Morning   (6AM  - 11AM)'),
        ('afternoon', 'Afternoon (11AM - 3PM)'),
        ('evening',   'Evening   (3PM  - 7PM)'),
        ('night',     'Night     (7PM  - 11PM)'),
    ]
    name       = models.CharField(max_length=20, choices=SLOT_CHOICES, unique=True)
    start_time = models.TimeField()
    end_time   = models.TimeField()

    def __str__(self):
        return self.get_name_display()


# ─── FOOD ITEM ───
class FoodItem(models.Model):
    category          = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='food_items')
    name              = models.CharField(max_length=200)
    description       = models.TextField(blank=True)
    selling_price     = models.DecimalField(max_digits=8, decimal_places=2)
    # ADMIN ONLY
    preparation_cost  = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    ingredients       = models.TextField(blank=True)
    # image             = models.ImageField(upload_to='food_images/')
    image             = models.ImageField(upload_to='food_images/', blank=True, null=True)
    # image_url         = models.URLField(help_text="Unsplash URL")
    preparation_time  = models.PositiveIntegerField(help_text="Time in minutes")
    is_veg            = models.BooleanField(default=True)
    available_slots   = models.ManyToManyField(TimeSlot, blank=True)
    serves            = models.CharField(max_length=50, default='1 person')
    is_available      = models.BooleanField(default=True)
    is_todays_special = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['category', 'name']
    def __str__(self):
        return self.name
    @property
    def profit_margin(self):
        return self.selling_price - self.preparation_cost


# ─── CUSTOM FOOD REQUEST ───
class CustomFoodRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('accepted',  'Accepted'),
        ('cancelled', 'Cancelled'),
    ]
    customer    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_requests')
    food_name   = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    accepted_by = models.ForeignKey(
                    'chefs.ChefProfile', on_delete=models.SET_NULL,
                    null=True, blank=True, related_name='accepted_requests')
    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField()

    def __str__(self):
        return f"Request: {self.food_name} by {self.customer.username}"


# ─── ORDER ───
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending - Waiting for Chef'),
        ('accepted',  'Accepted - Chef Accepted'),
        ('preparing', 'Preparing - Chef is Cooking'),
        ('ready',     'Ready - Food is Ready'),
        ('picked_up', 'Picked Up'),
        ('on_way',    'On The Way'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('cod',    'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]

    customer             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    chef                 = models.ForeignKey(
                            'chefs.ChefProfile', on_delete=models.SET_NULL,
                            null=True, blank=True, related_name='orders')
    delivery_boy         = models.ForeignKey(
                            'delivery.DeliveryBoyProfile', on_delete=models.SET_NULL,
                            null=True, blank=True, related_name='orders')

    status               = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method       = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    payment_status       = models.CharField(max_length=20, default='pending')

    total_amount         = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address     = models.TextField()
    delivery_lat         = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_lng         = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_number       = models.CharField(max_length=15)
    special_instructions = models.TextField(blank=True)

    # OTP for delivery confirmation
    otp                  = models.CharField(max_length=6, blank=True)
    otp_verified         = models.BooleanField(default=False)

    # Timestamps
    created_at           = models.DateTimeField(auto_now_add=True)
    accepted_at          = models.DateTimeField(null=True, blank=True)
    ready_at             = models.DateTimeField(null=True, blank=True)
    picked_up_at         = models.DateTimeField(null=True, blank=True)
    delivered_at         = models.DateTimeField(null=True, blank=True)

    # Payment release by admin
    chef_payment_released     = models.BooleanField(default=False)
    delivery_payment_released = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} - {self.status}"


# ─── ORDER ITEMS ───
class OrderItem(models.Model):
    order     = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField(default=1)
    price     = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity


# ─── ORDER STATUS HISTORY ───
class OrderStatusHistory(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status     = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note       = models.TextField(blank=True)

    class Meta:
        ordering = ['changed_at']

    def __str__(self):
        return f"Order #{self.order.id} → {self.status}"


# ─── NOTIFICATION ───
class Notification(models.Model):
    TYPE_CHOICES = [
        ('order_placed',     'Order Placed'),
        ('order_accepted',   'Order Accepted'),
        ('food_ready',       'Food Ready'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered',        'Delivered'),
        ('cancelled',        'Cancelled'),
        ('payment',          'Payment'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type       = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    order      = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} → {self.user.username}"


# ─── RATING ───
class Rating(models.Model):
    order           = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='rating')
    customer        = models.ForeignKey(User, on_delete=models.CASCADE)
    chef_rating     = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    chef_review     = models.TextField(blank=True)
    delivery_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    delivery_review = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating for Order #{self.order.id}"