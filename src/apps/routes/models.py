from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
    street = models.CharField(max_length=128)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64, null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    country = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Route(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    distance = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # km
    duration = models.PositiveIntegerField(default=0, blank=True)  # sec


class RoutePoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    sequence_number = models.PositiveIntegerField(blank=True, null=True)  # number in order
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    arrival_time = models.TimeField(null=True, blank=True)
    # departure_time = models.TimeField(null=True, blank=True)
    