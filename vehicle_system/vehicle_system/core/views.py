# core/views.py
from django.shortcuts import render  # Added for index view
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, TrafficLaw, Offense, Payment, Registration, State, Fine
from .serializers import (
    VehicleSerializer, TrafficLawSerializer, OffenseSerializer,
    PaymentSerializer, RegistrationSerializer, StateSerializer,
    UserSerializer, FineSerializer
)

User = get_user_model()

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def index(request):
    """Serve the HTMX frontend."""
    return render(request, 'index.html')

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['registered_state']

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user).select_related('owner', 'registered_state').order_by('plate_number')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrafficLawViewSet(viewsets.ModelViewSet):
    queryset = TrafficLaw.objects.order_by('law_name')
    serializer_class = TrafficLawSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

class OffenseViewSet(viewsets.ModelViewSet):
    serializer_class = OffenseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['state', 'status']

    def get_queryset(self):
        return Offense.objects.filter(user=self.request.user).select_related('vehicle', 'user', 'law', 'state').order_by('offense_date')

class FineViewSet(viewsets.ModelViewSet):
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        return Fine.objects.filter(user=self.request.user).select_related('user', 'offense').order_by('issued_at')

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['fine']

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('user', 'fine').order_by('payment_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            payment = serializer.save(user=request.user)
            fine = payment.fine
            if fine.amount <= payment.amount:
                fine.status = "paid"
                fine.save()
                fine.offense.status = "paid"
                fine.offense.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['state']

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user).select_related('vehicle', 'user', 'state').order_by('registration_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.order_by('name')
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated]

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        # Restrict to the authenticated user only (non-admins see only themselves)
        if self.request.user.is_staff:
            return User.objects.order_by('username')  # Admins see all users
        return User.objects.filter(id=self.request.user.id).order_by('username')