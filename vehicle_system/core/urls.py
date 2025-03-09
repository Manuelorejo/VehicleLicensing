from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    index, VehicleViewSet, TrafficLawViewSet, OffenseViewSet,
    FineViewSet, PaymentViewSet, RegistrationViewSet, StateViewSet, UserViewSet,
    UserRegistrationView
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

urlpatterns = [
    path('', index, name='index'),  # Serve index.html at /api/
    path('auth/login/', obtain_auth_token, name='login'),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
] + router.urls