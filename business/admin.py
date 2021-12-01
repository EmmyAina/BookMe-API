from django.contrib import admin
from .models import BusinessOwner, Bookings

# Register your models here.
admin.site.register((BusinessOwner, Bookings))
