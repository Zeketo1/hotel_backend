from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from django.utils import timezone
from django.db.models import Q

from .validators import validate_image_url

class CustomUser(AbstractUser):
    # Add email field with unique=True (overrides AbstractUser's email)
    email = models.EmailField(unique=True, verbose_name='email address')  # <-- Add this line

    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    phone = models.CharField(max_length=15, blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions",
        related_query_name="user",
    )

class Room(models.Model):
    type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    max_guests = models.PositiveIntegerField(default=2)  # New field
    image_url = models.URLField(max_length=500, validators=[validate_image_url])
    image = models.ImageField(upload_to='rooms/', null=True, blank=True)  # New field

    @property
    def is_available(self):
        # Check if there are no approved/pending bookings overlapping with today
        today = timezone.now().date()
        return not self.booking_set.filter(
            Q(status='approved') | Q(status='pending'),
            check_in__lte=today,
            check_out__gte=today
        ).exists()
    
class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (${self.price})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    services = models.ManyToManyField(Service, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.email} - {self.room.type}"