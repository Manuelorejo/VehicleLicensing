# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Vehicle, TrafficLaw, Offense, Payment, Registration, State, Fine
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'password']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            password=validated_data['password']
        )
        return user

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']

class VehicleSerializer(serializers.ModelSerializer):
    registered_state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'vin', 'make', 'model', 'year', 'registered_state']

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            owner = request.user
            if owner.fines.filter(status="unpaid").exists():
                raise serializers.ValidationError("You cannot register a vehicle until all fines are paid.")
        return data

    def validate_year(self, value):
        current_year = timezone.now().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError(f"Year must be between 1900 and {current_year + 1}.")
        return value

class TrafficLawSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficLaw
        fields = ['law_name', 'description', 'fine_amount']

class OffenseSerializer(serializers.ModelSerializer):
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    class Meta:
        model = Offense
        fields = ['vehicle', 'user', 'law', 'offense_date', 'state', 'fine_amount', 'status']

class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = ['id', 'user', 'offense', 'amount', 'issued_at', 'status']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'fine', 'registration', 'amount', 'transaction_id', 'payment_date', 'payment_type']
        read_only_fields = ['user', 'payment_date']

    def validate(self, data):
        # Ensure exactly one of fine or registration is provided
        if data.get('fine') and data.get('registration'):
            raise serializers.ValidationError("Payment must be associated with either a fine or a registration, not both.")
        if not data.get('fine') and not data.get('registration'):
            raise serializers.ValidationError("Payment must be associated with either a fine or a registration.")
        return data

    def create(self, validated_data):
        # Automatically set the user and payment_type
        validated_data['user'] = self.context['request'].user
        if validated_data.get('registration'):
            validated_data['payment_type'] = 'renewal'
        return Payment.objects.create(**validated_data)

class RegistrationSerializer(serializers.ModelSerializer):
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    user = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(), read_only=True) 
    class Meta:
        model = Registration
        fields = ['vehicle', 'user', 'state', 'registration_date', 'expiry_date']
        read_only_fields = ['registration_date']

    def validate_expiry_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Expiry date cannot be in the past.")
        return value
    
from .models import CarMake, CarModel

class CarMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarMake
        fields = ['id', 'name']

class CarModelSerializer(serializers.ModelSerializer):
    make = CarMakeSerializer(read_only=True)
    class Meta:
        model = CarModel
        fields = ['id', 'name', 'make']    