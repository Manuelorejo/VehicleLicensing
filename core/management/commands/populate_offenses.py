from django.core.management.base import BaseCommand
from core.models import TrafficLaw, Offense, Vehicle, State
from django.contrib.auth import get_user_model
from decimal import Decimal
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates TrafficLaw and creates sample Offense records'

    def handle(self, *args, **kwargs):
        # Create traffic laws
        traffic_laws_data = [
            {"law_name": "Speed Limit Violation", "fine_amount": Decimal("100000.00")},
            {"law_name": "Driving Without a Valid License", "fine_amount": Decimal("10000.00")},
            {"law_name": "Driving Without a Seat Belt", "fine_amount": Decimal("2000.00")},
            {"law_name": "Using Phone While Driving", "fine_amount": Decimal("4000.00")},
            {"law_name": "Driving Without a Speed Limiting Device", "fine_amount": Decimal("50000.00")},
            {"law_name": "Overloading", "fine_amount": Decimal("50000.00")},
            {"law_name": "Underage Driving", "fine_amount": Decimal("2000.00")},
            {"law_name": "Driving With Worn-Out Tyres", "fine_amount": Decimal("3000.00")},
            {"law_name": "Failure to Report an Accident", "fine_amount": Decimal("20000.00")},
            {"law_name": "Dangerous Driving", "fine_amount": Decimal("50000.00")},
            {"law_name": "Driving Without a Fire Extinguisher", "fine_amount": Decimal("3000.00")},
            {"law_name": "Disobeying Traffic Lights", "fine_amount": Decimal("20000.00")},
            {"law_name": "Wrongful Overtaking", "fine_amount": Decimal("5000.00")},
            {"law_name": "Driving Without Spare Tyre", "fine_amount": Decimal("3000.00")},
            {"law_name": "Operating Vehicle With Forged Documents", "fine_amount": Decimal("20000.00")},
        ]

        # Populate TrafficLaw
        for law_data in traffic_laws_data:
            TrafficLaw.objects.get_or_create(
                law_name=law_data["law_name"],
                defaults={"fine_amount": law_data["fine_amount"]}
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added {law_data["law_name"]} - NGN {law_data["fine_amount"]}'))

        # Create sample Offense (requires a vehicle, user, and state)
        try:
            user = User.objects.get(username='admin')
            state = State.objects.get(name='Lagos')
            vehicle = Vehicle.objects.get_or_create(
                owner=user,
                state=state,
                plate_number='ABC123',
                vin='VIN123456789',
                make='Toyota',
                model='Corolla',
                year=2020
            )[0]

            # Create one sample offense
            law = TrafficLaw.objects.get(law_name="Speed Limit Violation")
            Offense.objects.get_or_create(
                vehicle=vehicle,
                user=user,
                law=law,
                offense_date=datetime.datetime.now(),
                state=state,
                fine_amount=law.fine_amount,
                status="unpaid"
            )
            self.stdout.write(self.style.SUCCESS('Successfully added sample Speed Limit Violation for ABC123'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating sample offense: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Traffic laws and sample offense populated!'))