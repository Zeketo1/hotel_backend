from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import CustomUser, Room, Booking

# --------------------------
# General Model Serializers (for User, Room, Booking)
# --------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'role']

class RoomSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)  # Computed field
    class Meta:
        model = Room
        fields = '__all__'
        extra_kwargs = {
            'image_url': {'required': True}  # Make URL mandatory
        }

class BookingSerializer(serializers.ModelSerializer):
    # For writing/input: Accept room ID
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        write_only=True
    )
    
    # For reading/output: Show full room details
    room_detail = RoomSerializer(source='room', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 
            'user', 
            'room',          # For input (write)
            'room_detail',   # For output (read)
            'check_in', 
            'check_out', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['user', 'status', 'created_at', 'room_detail']

    def validate(self, data):
        # Existing date validation
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )
        
        # Add room availability check
        room = data['room']
        if not room.is_available:
            raise serializers.ValidationError(
                "This room is not available for the selected dates"
            )
            
        return data

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