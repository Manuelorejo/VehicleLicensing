# core/views.py
from django.shortcuts import render  # Added for index view
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Fine
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, TrafficLaw, Offense, Payment, Registration, State, Fine, CarMake, CarModel
from .serializers import (
    VehicleSerializer, TrafficLawSerializer, OffenseSerializer,
    PaymentSerializer, RegistrationSerializer, StateSerializer,
    UserSerializer, FineSerializer, CarMakeSerializer, CarModelSerializer
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
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

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

    @action(detail=True, methods=['GET'], url_path='check-eligibility')
    def check_eligibility(self, request, pk=None):
        registration = self.get_object()
        vehicle = registration.vehicle
        
        # Check for outstanding fines
        unpaid_fines = Fine.objects.filter(vehicle=vehicle, status='unpaid')
        if unpaid_fines.exists():
            return Response({
                'eligible': False,
                'reason': 'You have unpaid fines. Please settle them before renewing.'
            }, status=400)
        return Response({'eligible': True})
    
    def partial_update(self, request, *args, **kwargs):
        # Handle PATCH requests for updating expiry_date
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        eligibility_response = self.check_eligibility(request, pk=instance.id)
        if not eligibility_response.data['eligible']:
            return Response(eligibility_response.data, status=400)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Optional: Add validation (e.g., new expiry date must be in the future)
        if 'expiry_date' in request.data:
            from datetime import datetime
            new_expiry = datetime.strptime(request.data['expiry_date'], '%Y-%m-%d').date()
            if new_expiry <= datetime.today().date():
                return Response({'error': 'New expiry date must be in the future'}, status=400)
        
        serializer.save()
        return Response(serializer.data)
    
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
    
class CarMakeViewSet(viewsets.ModelViewSet):
    queryset = CarMake.objects.all()
    serializer_class = CarMakeSerializer
    permission_classes = [IsAuthenticated]

class CarModelViewSet(viewsets.ModelViewSet):
    serializer_class = CarModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CarModel.objects.all()
        make_id = self.request.query_params.get('make_id', None)
        if make_id is not None:
            queryset = queryset.filter(make_id=make_id)
        return queryset    

# Add to core/views.py
class LicenseTypeViewSet(viewsets.ModelViewSet):
    queryset = LicenseType.objects.order_by('name')
    serializer_class = LicenseTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

class LicenseViewSet(viewsets.ModelViewSet):
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['state', 'status', 'license_type']

    def get_queryset(self):
        return License.objects.filter(user=self.request.user).select_related('user', 'state', 'license_type').order_by('-issue_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LicenseRenewalViewSet(viewsets.ModelViewSet):
    serializer_class = LicenseRenewalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['license']

    def get_queryset(self):
        return LicenseRenewal.objects.filter(user=self.request.user).select_related('user', 'license').order_by('-renewed_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Add to LicenseViewSet in core/views.py
def list(self, request, *args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())
    page = self.paginate_queryset(queryset)
    
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        data = serializer.data
    else:
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
    
    # Check if request is from HTMX
    if request.headers.get('HX-Request'):
        # Build HTML response for HTMX
        html_response = '<h2>My Licenses</h2>'
        if not data:
            html_response += '<p>You have no licenses. Apply for one below.</p>'
        else:
            for license in data:
                status_class = 'text-success' if license['status'] == 'active' else 'text-danger'
                expiry_date = license['expiry_date']
                # Format date
                expiry_date = expiry_date.split('T')[0] if 'T' in expiry_date else expiry_date
                
                html_response += f'''
                <div class="card">
                    <div class="card-header">
                        <strong>License #{license['license_number']}</strong>
                        <span class="{status_class}">{license['status'].title()}</span>
                    </div>
                    <div class="card-body">
                        <div>Type: {license['license_type']}</div>
                        <div>Issued: {license['issue_date'].split('T')[0]}</div>
                        <div>Expires: {expiry_date}</div>
                    </div>
                    <div class="card-footer">
                        <button id="renew-license-{license['id']}" 
                                class="btn btn-sm btn-primary">Renew License</button>
                    </div>
                </div>
                '''
        
        # Add button to apply for a new license
        html_response += '''
        <div class="mt-4">
            <button hx-get="/api/license-types/" 
                    hx-headers='{"Authorization": "Token ' + request.auth.key + '"}' 
                    hx-target="#content">Apply for New License</button>
        </div>
        '''
        
        return Response(html_response)
    
    # Normal API response
    return Response(data)