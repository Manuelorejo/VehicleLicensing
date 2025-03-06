from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    index, VehicleViewSet, TrafficLawViewSet, OffenseViewSet,
    FineViewSet, PaymentViewSet, RegistrationViewSet, StateViewSet, UserViewSet
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'traffic-laws', TrafficLawViewSet)
router.register(r'offenses', OffenseViewSet)
router.register(r'fines', FineViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'registrations', RegistrationViewSet)
router.register(r'states', StateViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', index, name='index'),  # Serve index.html at /api/
    path('auth/login/', obtain_auth_token, name='login'),
] + router.urls