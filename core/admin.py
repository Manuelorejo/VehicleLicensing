from django.contrib import admin
from .models import User, Vehicle, Fine, Offense, TrafficLaw, State, Registration, Payment, Fine, AuditLog

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ("user", "offense", "amount", "status", "issued_at")  # Replace "paid" with "status"
    list_filter = ("status", "issued_at")
    search_fields = ("user__username", "offense__law__law_name", "amount")

admin.site.register(User)
admin.site.register(Vehicle)
admin.site.register(Offense)
admin.site.register(TrafficLaw)
admin.site.register(State)
admin.site.register(Registration)
admin.site.register(Payment)
admin.site.register(AuditLog)
