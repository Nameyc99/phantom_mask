from django.db import models
from django.utils import timezone

class User(models.Model):
    name = models.CharField(max_length=255)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Pharmacy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Mask(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='masks')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='transactions')
    mask = models.ForeignKey(Mask, on_delete=models.CASCADE, related_name='transactions')
    transaction_date = models.DateTimeField(default=timezone.now)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.name} - {self.transaction_amount}"


class PharmacyOpeningHour(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='opening_hours')
    day_of_week = models.CharField(max_length=3)  # Mon, Tue, etc.
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.pharmacy.name} - {self.day_of_week}"
