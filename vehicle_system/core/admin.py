from django.contrib import admin
from .models import User, Vehicle, Fine, Offense, TrafficLaw, State, Registration, Payment, Fine, AuditLog

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ("user", "offense", "amount", "status", "issued_at")  # Replace "paid" with "status"
    list_filter = ("status", "issued_at")
    search_fields = ("user__username", "offense__law__law_name", "amount")

# Add to core/admin.py
from .models import LicenseType, License, LicenseRenewal

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('license_number', 'user', 'license_type', 'state', 'status', 'expiry_date')
    list_filter = ('status', 'license_type', 'state')
    search_fields = ('license_number', 'user__username')

admin.site.register(LicenseType)
admin.site.register(LicenseRenewal)
admin.site.register(User)
admin.site.register(Vehicle)
admin.site.register(Offense)
admin.site.register(TrafficLaw)
admin.site.register(State)
admin.site.register(Registration)
admin.site.register(Payment)
admin.site.register(AuditLog)
