from django.db import models
from django.contrib.auth.models import User


# ─── DELIVERY BOY PROFILE ───
class DeliveryBoyProfile(models.Model):
    VEHICLE_CHOICES = [
        ('bike',    'Bike'),
        ('scooter', 'Scooter'),
        ('bicycle', 'Bicycle'),
    ]
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_profile')
    phone          = models.CharField(max_length=15, unique=True)
    profile_photo  = models.URLField(blank=True)
    # Address
    address        = models.TextField()
    city           = models.CharField(max_length=100)
    pincode        = models.CharField(max_length=10)
    # Documents - admin only
    pan_number     = models.CharField(max_length=10, blank=True)
    licence_number = models.CharField(max_length=20, blank=True)
    # Vehicle
    vehicle_type   = models.CharField(max_length=10, choices=VEHICLE_CHOICES, default='bike')
    vehicle_number = models.CharField(max_length=20, blank=True)
    # Bank details
    account_holder = models.CharField(max_length=200, blank=True)
    bank_name      = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    ifsc_code      = models.CharField(max_length=11, blank=True)
    upi_id         = models.CharField(max_length=100, blank=True)
    # Status
    is_approved    = models.BooleanField(default=False)
    is_online      = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)
    # Rating
    total_rating   = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews  = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Delivery: {self.user.get_full_name() or self.user.username}"
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    @property
    def average_rating(self):
        if self.total_reviews == 0:
            return 0
        return round(self.total_rating / self.total_reviews, 1)

# ─── DELIVERY ASSIGNMENT ───
class DeliveryAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned',  'Assigned'),
        ('picked_up', 'Picked Up'),
        ('on_way',    'On the Way'),
        ('delivered', 'Delivered'),
    ]

    delivery_boy   = models.ForeignKey(DeliveryBoyProfile, on_delete=models.CASCADE, related_name='assignments')
    order          = models.OneToOneField('core.Order', on_delete=models.CASCADE, related_name='delivery_assignment')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')

    # Locations
    pickup_address = models.TextField()
    pickup_lat     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_lng     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    drop_address   = models.TextField()
    drop_lat       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    drop_lng       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Timestamps
    assigned_at    = models.DateTimeField(auto_now_add=True)
    picked_up_at   = models.DateTimeField(null=True, blank=True)
    delivered_at   = models.DateTimeField(null=True, blank=True)

    # COD
    cod_amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cod_collected  = models.BooleanField(default=False)
    cod_submitted  = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery #{self.order.id} by {self.delivery_boy.full_name}"


# ─── DELIVERY EARNINGS ───
class DeliveryEarnings(models.Model):
    delivery_boy = models.ForeignKey(DeliveryBoyProfile, on_delete=models.CASCADE, related_name='earnings')
    order        = models.OneToOneField('core.Order', on_delete=models.CASCADE, related_name='delivery_earning')
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid      = models.BooleanField(default=False)
    paid_at      = models.DateTimeField(null=True, blank=True)
    date         = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.delivery_boy.full_name} - ₹{self.amount} - {'Paid' if self.is_paid else 'Pending'}"


# ─── DAILY CASH SUMMARY ───
class DailyCashSummary(models.Model):
    delivery_boy    = models.ForeignKey(DeliveryBoyProfile, on_delete=models.CASCADE, related_name='cash_summaries')
    date            = models.DateField()
    total_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_submitted = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_settled      = models.BooleanField(default=False)

    class Meta:
        unique_together = ('delivery_boy', 'date')

    def __str__(self):
        return f"{self.delivery_boy.full_name} - {self.date}"
    @property
    def pending_amount(self):
        return self.total_collected - self.total_submitted