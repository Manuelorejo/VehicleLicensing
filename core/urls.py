from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    index, VehicleViewSet, TrafficLawViewSet, OffenseViewSet,
    FineViewSet, PaymentViewSet, RegistrationViewSet, StateViewSet, UserViewSet,
    UserRegistrationView,CarMakeViewSet, CarModelViewSet
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'traffic-laws', TrafficLawViewSet, basename='trafficlaw')
router.register(r'offenses', OffenseViewSet, basename='offense')
router.register(r'fines', FineViewSet, basename='fine')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'registrations', RegistrationViewSet, basename='registration')
router.register(r'states', StateViewSet, basename='state')
router.register(r'users', UserViewSet, basename='user')
router.register(r'car-makes', CarMakeViewSet, basename='car-makes')
router.register(r'car-models', CarModelViewSet, basename='car-models')

urlpatterns = [
    path('', index, name='index'),  # Serve index.html at /api/
    path('auth/login/', obtain_auth_token, name='login'),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
] + router.urls

# Add to core/urls.py
from .views import (
    index, VehicleViewSet, TrafficLawViewSet, OffenseViewSet,
    FineViewSet, PaymentViewSet, RegistrationViewSet, StateViewSet, UserViewSet,
    LicenseTypeViewSet, LicenseViewSet, LicenseRenewalViewSet  # Add these
)

router = DefaultRouter()
# Existing routes
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'traffic-laws', TrafficLawViewSet)
router.register(r'offenses', OffenseViewSet, basename='offense')
router.register(r'fines', FineViewSet, basename='fine')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'registrations', RegistrationViewSet, basename='registration')
router.register(r'states', StateViewSet)
router.register(r'users', UserViewSet, basename='user')

# New routes for licenses
router.register(r'license-types', LicenseTypeViewSet)
router.register(r'licenses', LicenseViewSet, basename='license')
router.register(r'license-renewals', LicenseRenewalViewSet, basename='license-renewal')