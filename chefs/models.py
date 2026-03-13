from django.db import models
from django.contrib.auth.models import User
from core.models import FoodItem, TimeSlot


# ─── CUISINE TYPE ───
class CuisineType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ─── CHEF PROFILE ───
class ChefProfile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    user               = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chef_profile')
    phone              = models.CharField(max_length=15, unique=True)
    gender             = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth      = models.DateField(null=True, blank=True)
    profile_photo      = models.URLField(blank=True)

    # Address
    address            = models.TextField()
    city               = models.CharField(max_length=100)
    state              = models.CharField(max_length=100)
    pincode            = models.CharField(max_length=10)
    latitude           = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude          = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Food details
    cuisine_types      = models.ManyToManyField(CuisineType, blank=True)
    is_vegetarian      = models.BooleanField(default=False)
    is_non_vegetarian  = models.BooleanField(default=True)
    is_vegan           = models.BooleanField(default=False)
    experience_years   = models.PositiveIntegerField(default=0)
    bio                = models.TextField(blank=True, max_length=500)
    languages          = models.CharField(max_length=200, blank=True)

    # Availability
    available_slots    = models.ManyToManyField(TimeSlot, blank=True)
    available_days     = models.CharField(max_length=100, blank=True)
    max_orders_per_slot = models.PositiveIntegerField(default=5)

    # Kitchen photos
    kitchen_photo1     = models.URLField(blank=True)
    kitchen_photo2     = models.URLField(blank=True)
    kitchen_photo3     = models.URLField(blank=True)

    # KYC - admin only
    aadhaar_number     = models.CharField(max_length=12, blank=True)
    pan_number         = models.CharField(max_length=10, blank=True)

    # Status
    is_approved        = models.BooleanField(default=False)
    is_online          = models.BooleanField(default=False)
    is_active          = models.BooleanField(default=True)

    # Rating
    total_rating       = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews      = models.PositiveIntegerField(default=0)

    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chef: {self.user.get_full_name() or self.user.username}"

    @property
    def average_rating(self):
        if self.total_reviews == 0:
            return 0
        return round(self.total_rating / self.total_reviews, 1)

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


# ─── CHEF BANK DETAILS ───
class ChefBankDetails(models.Model):
    chef           = models.OneToOneField(ChefProfile, on_delete=models.CASCADE, related_name='bank_details')
    account_holder = models.CharField(max_length=200)
    bank_name      = models.CharField(max_length=200)
    account_number = models.CharField(max_length=20)
    ifsc_code      = models.CharField(max_length=11)
    upi_id         = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Bank: {self.chef.full_name}"


# ─── CHEF DISH ───
class ChefDish(models.Model):
    chef             = models.ForeignKey(ChefProfile, on_delete=models.CASCADE, related_name='dishes')
    food_item        = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='chef_dishes')
    custom_price     = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # ADMIN ONLY
    preparation_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    ingredients      = models.TextField(blank=True)

    is_available     = models.BooleanField(default=True)
    available_slots  = models.ManyToManyField(TimeSlot, blank=True)

    def __str__(self):
        return f"{self.food_item.name} by {self.chef.full_name}"

    @property
    def price(self):
        return self.custom_price or self.food_item.selling_price


# ─── TODAY'S SPECIAL ───
class TodaysSpecial(models.Model):
    chef        = models.ForeignKey(ChefProfile, on_delete=models.CASCADE, related_name='todays_specials')
    dish        = models.ForeignKey(ChefDish, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    date        = models.DateField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return f"Today's Special: {self.dish.food_item.name} by {self.chef.full_name}"


# ─── CHEF EARNINGS ───
class ChefEarnings(models.Model):
    chef     = models.ForeignKey(ChefProfile, on_delete=models.CASCADE, related_name='earnings')
    order    = models.OneToOneField('core.Order', on_delete=models.CASCADE, related_name='chef_earning')
    amount   = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid  = models.BooleanField(default=False)
    paid_at  = models.DateTimeField(null=True, blank=True)
    date     = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.chef.full_name} - ₹{self.amount} - {'Paid' if self.is_paid else 'Pending'}"


# ─── FAVOURITE CHEF ───
class FavouriteChef(models.Model):
    customer   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite_chefs')
    chef       = models.ForeignKey(ChefProfile, on_delete=models.CASCADE, related_name='favourited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'chef')

    def __str__(self):
        return f"{self.customer.username} ❤️ {self.chef.full_name}"