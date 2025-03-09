from django.core.management.base import BaseCommand
from core.models import CarMake, CarModel

class Command(BaseCommand):
    help = 'Populates CarMake and CarModel with common car makes and models'

    def handle(self, *args, **kwargs):
        car_data = {
            'Toyota': ['Corolla', 'Camry', 'RAV4', 'Hilux', 'Yaris'],
            'Honda': ['Civic', 'Accord', 'CR-V', 'Fit', 'Pilot'],
            'Ford': ['Focus', 'Mustang', 'Explorer', 'F-150', 'Escape'],
            'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'GLC', 'GLE'],
            'BMW': ['3 Series', '5 Series', 'X3', 'X5', '7 Series'],
            'Volkswagen': ['Golf', 'Passat', 'Tiguan', 'Jetta', 'Polo'],
            'Nissan': ['Altima', 'Sentra', 'Rogue', 'Patrol', 'Navara'],
            'Hyundai': ['Tucson', 'Elantra', 'Santa Fe', 'Accent', 'Sonata'],
            'Kia': ['Sportage', 'Rio', 'Sorento', 'Optima', 'Picanto'],
            'Peugeot': ['206', '307', '508', '3008', '5008'],
        }

        for make_name, models in car_data.items():
            make, created = CarMake.objects.get_or_create(name=make_name)
            self.stdout.write(self.style.SUCCESS(f'Added make: {make_name}'))
            for model_name in models:
                CarModel.objects.get_or_create(make=make, name=model_name)
                self.stdout.write(self.style.SUCCESS(f'  Added model: {model_name} for {make_name}'))

        self.stdout.write(self.style.SUCCESS('All car makes and models have been populated!'))