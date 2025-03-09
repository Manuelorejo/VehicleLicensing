# core/tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Vehicle, TrafficLaw, Offense, Payment, Fine, State, Registration
import datetime

User = get_user_model()

class VehicleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', phone='1234567890')
        self.state = State.objects.create(name='Lagos')
        self.client.login(username='testuser', password='password123')
        self.url = '/api/vehicles/'

    def test_create_vehicle(self):
        data = {
            'plate_number': 'ABC123',
            'vin': 'VIN123',
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'registered_state': self.state.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.count(), 1)
        self.assertEqual(Vehicle.objects.first().owner, self.user)

    def test_create_vehicle_with_unpaid_fines(self):
        traffic_law = TrafficLaw.objects.create(law_name='Speeding', fine_amount=5000, description='Speeding violation')
        vehicle = Vehicle.objects.create(
            plate_number='XYZ123', vin='VINXYZ', make='Toyota', model='Camry',
            year=2021, owner=self.user, registered_state=self.state
        )
        offense = Offense.objects.create(
            vehicle=vehicle, user=self.user, law=traffic_law,
            offense_date='2025-02-15T00:00:00Z', state=self.state, fine_amount=5000
        )
        Fine.objects.create(user=self.user, offense=offense, amount=5000)
        data = {
            'plate_number': 'ABC123',
            'vin': 'VIN123',
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'registered_state': self.state.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You cannot register a vehicle until all fines are paid', str(response.data))

    def test_create_vehicle_duplicate_plate(self):
        Vehicle.objects.create(
            plate_number='ABC123', vin='VINXYZ', make='Toyota', model='Camry',
            year=2021, owner=self.user, registered_state=self.state
        )
        data = {
            'plate_number': 'ABC123',
            'vin': 'VIN123',
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'registered_state': self.state.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('plate_number', str(response.data))

    def test_get_vehicles(self):
        Vehicle.objects.create(
            plate_number='XYZ123', vin='VINXYZ', make='Toyota', model='Camry',
            year=2021, owner=self.user, registered_state=self.state
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class TrafficLawTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', phone='1234567890')
        self.client.login(username='testuser', password='password123')
        self.url = '/api/traffic-laws/'

    def test_create_traffic_law(self):
        data = {
            'law_name': 'Speeding',
            'description': 'Exceeding the speed limit.',
            'fine_amount': 10000.00
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TrafficLaw.objects.count(), 1)

    def test_get_traffic_laws(self):
        TrafficLaw.objects.create(
            law_name='Speeding',
            description='Exceeding the speed limit.',
            fine_amount=10000.00
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', phone='1234567890')
        self.state = State.objects.create(name='Lagos')
        self.client.login(username='testuser', password='password123')
        self.url = '/api/payments/'
        self.vehicle = Vehicle.objects.create(
            plate_number='XYZ123', vin='VINXYZ', make='Toyota', model='Camry',
            year=2021, owner=self.user, registered_state=self.state
        )
        self.traffic_law = TrafficLaw.objects.create(
            law_name='Running Red Light',
            description='Failing to stop at a red light.',
            fine_amount=5000.00
        )
        self.offense = Offense.objects.create(
            vehicle=self.vehicle, user=self.user, law=self.traffic_law,
            offense_date='2025-02-15T00:00:00Z', state=self.state, fine_amount=5000.00
        )
        self.fine = Fine.objects.create(user=self.user, offense=self.offense, amount=5000)

    def test_create_payment(self):
        data = {
            'fine': self.fine.id,
            'amount': 5000.00,
            'transaction_id': 'TXN1234'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        self.fine.refresh_from_db()
        self.assertEqual(self.fine.status, 'paid')

    def test_create_payment_exceeding_fine(self):
        data = {
            'fine': self.fine.id,
            'amount': 6000.00,
            'transaction_id': 'TXN1234'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot exceed fine amount', str(response.data))

    def test_get_payments(self):
        Payment.objects.create(
            user=self.user, fine=self.fine, amount=5000.00,
            transaction_id='TXN1234'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class RegistrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', phone='1234567890')
        self.state = State.objects.create(name='Lagos')
        self.vehicle = Vehicle.objects.create(
            plate_number='XYZ123', vin='VINXYZ', make='Toyota', model='Camry',
            year=2021, owner=self.user, registered_state=self.state
        )
        self.client.login(username='testuser', password='password123')
        self.url = '/api/registrations/'

    def test_create_registration(self):
        data = {
            'vehicle': self.vehicle.id,
            'state': self.state.id,
            'expiry_date': '2026-02-24T00:00:00Z'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Registration.objects.count(), 1)

    def test_create_registration_past_expiry(self):
        data = {
            'vehicle': self.vehicle.id,
            'state': self.state.id,
            'expiry_date': '2024-02-24T00:00:00Z'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot be in the past', str(response.data))