from django.contrib import admin
from .models import CustomUser, Room, Booking  # Import your models

# Register models here
admin.site.register(CustomUser)
admin.site.register(Room)
admin.site.register(Booking)