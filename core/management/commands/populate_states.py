from django.core.management.base import BaseCommand
from core.models import State

class Command(BaseCommand):
    help = 'Populates the State model with all Nigerian states and FCT'

    def handle(self, *args, **kwargs):
        # List of all 36 states in Nigeria + FCT
        nigerian_states = [
            'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa',
            'Benue', 'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo',
            'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo', 'Jigawa',
            'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
            'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun',
            'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
        ]

        # Add states to the database
        for state_name in nigerian_states:
            State.objects.get_or_create(name=state_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully added {state_name}'))

        self.stdout.write(self.style.SUCCESS('All Nigerian states have been populated!'))