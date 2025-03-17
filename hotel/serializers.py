from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import CustomUser, Room, Booking, Service
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# --------------------------
# General Model Serializers (for User, Room, Booking)
# --------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'role', 'is_superuser']

class RoomSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)  # Computed field
    class Meta:
        model = Room
        fields = '__all__'
        extra_kwargs = {
            'image_url': {'required': True}  # Make URL mandatory
        }

User = get_user_model()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

def validate_password_strength(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, validators=[validate_password_strength], style={'input_type': 'password'})

class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status']  # Only include necessary fields
        read_only_fields = ['user', 'room', 'check_in', 'check_out']  # All other fields

class BookingSerializer(serializers.ModelSerializer):
    # For writing/input: Accept room ID
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        write_only=True
    )
    
    # For reading/output: Show full room details
    room_detail = RoomSerializer(source='room', read_only=True)

    services = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Service.objects.all(),
        required=False
    )

    class Meta:
        model = Booking
        fields = [
            'id', 
            'user', 
            'room',
            'room_detail',
            'check_in', 
            'check_out', 
            'status', 
            'created_at',
            'services', 
            'total_price'
        ]
        read_only_fields = ['user', 'status', 'created_at', 'room_detail']

    def validate(self, data):
        # Skip validation if check_in and check_out are not provided
        if 'check_in' not in data or 'check_out' not in data:
            return data
        
        # Date validation
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )
        
        # Room availability check
        room = data['room']
        if not room.is_available:
            raise serializers.ValidationError(
                "This room is not currently available"
            )
            
        return data

    def create(self, validated_data):
        # Extract services from validated data
        services = validated_data.pop('services', [])
        
        # Create booking instance
        booking = super().create(validated_data)
        
        # Add services and calculate price
        booking.services.set(services)
        
        # Calculate total price
        room_price = booking.room.price
        service_prices = sum(service.price for service in services)
        booking.total_price = room_price + service_prices
        booking.save()
        
        return booking

# --------------------------
# Authentication-Specific Serializers (for Registration/Login)
# --------------------------
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role', 'phone']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'guest'),
            phone=validated_data.get('phone', '')
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        request = self.context.get('request')

        if email and password:
            user = authenticate(request=request, email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials.")
        else:
            raise serializers.ValidationError("Email and password are required.")

        data['user'] = user
        return data