# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField(null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)

from django.db import models

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Vehicle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    plate_number = models.CharField(max_length=20, unique=True, db_index=True)
    vin = models.CharField(max_length=50, unique=True, db_index=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(timezone.now().year + 1)])
    registered_state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.owner.fines.filter(status="unpaid").exists():
            raise ValidationError("You cannot register a vehicle until all fines are paid.")
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.plate_number} - {self.owner.username}"

    class Meta:
        indexes = [models.Index(fields=['owner', 'plate_number'])]

class TrafficLaw(models.Model):
    law_name = models.CharField(max_length=255, unique=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.law_name

    class Meta:
        ordering = ['law_name']

class Offense(models.Model):
    # Define status choices as a class attribute for reusability
    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]

    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='offenses')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='offenses')
    law = models.ForeignKey('TrafficLaw', on_delete=models.CASCADE, related_name='offenses')
    offense_date = models.DateTimeField(db_index=True)
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    fine_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0'))]
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default="unpaid", 
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.law.law_name} ({self.offense_date.date()} in {self.state})"

    class Meta:
        ordering = ['-offense_date']  # Order by most recent offense first
        indexes = [
            models.Index(fields=['status']),  # Already added via db_index=True
            models.Index(fields=['state']),
        ]

class Fine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fines')
    offense = models.ForeignKey(Offense, on_delete=models.CASCADE, related_name="fines")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    issued_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=20, choices=[("unpaid", "Unpaid"), ("paid", "Paid")], default="unpaid")
    def __str__(self):
        return f"Fine of {self.amount} for {self.user.username}"

class Registration(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(db_index=True)
    def __str__(self):
        return f"Registration for {self.vehicle.plate_number}"

class Payment(models.Model):
    PAYMENT_TYPES = (
        ('fine', 'Fine Payment'),
        ('renewal', 'Renewal Payment'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    fine = models.ForeignKey(Fine, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    payment_date = models.DateTimeField(auto_now_add=True, db_index=True)
    transaction_id = models.CharField(max_length=50, unique=True, db_index=True)
    registration = models.ForeignKey('Registration', on_delete=models.SET_NULL, null=True, blank=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='fine')

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount}"

class AuditLog(models.Model):
    table_name = models.CharField(max_length=50)
    record_id = models.IntegerField()
    action = models.CharField(max_length=20, choices=[("INSERT", "Insert"), ("UPDATE", "Update"), ("DELETE", "Delete")])
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    def __str__(self):
        return f"{self.table_name} {self.action} at {self.timestamp}"

class CarMake(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class CarModel(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make.name} {self.name}"

    class Meta:
        ordering = ['name']
        unique_together = ['make', 'name']    