from django.shortcuts import render
from rest_framework import generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import Room, Booking, CustomUser, Service
from .serializers import (
    RoomSerializer, 
    BookingSerializer, 
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    BookingStatusSerializer, 
    PasswordResetSerializer, 
    PasswordResetConfirmSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import RetrieveAPIView
from django_rest_passwordreset.models import ResetPasswordToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
import os
from django.conf import settings
from django.template.exceptions import TemplateDoesNotExist

# -------------------------------------------------
# Existing Views (Rooms, Bookings, Users)
# -------------------------------------------------
class RoomList(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can create rooms

class RoomDetailView(RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer  # Use your actual serializer
    permission_classes = [permissions.IsAdminUser]

class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Get room ID from request data
        room_id = self.request.data.get('room')
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError("Invalid room ID")

        # Get service IDs from request data
        services_ids = self.request.data.get('services', [])
        print("Received Service IDs:", services_ids)
        
        # Save the booking with user and room
        booking = serializer.save(
            user=self.request.user,
            room=room
        )
        
        # Add services to booking
        if services_ids:
            try:
                services = Service.objects.filter(id__in=services_ids)
                print("Found Services:", list(services.values_list('id', flat=True)))
                if len(services) != len(services_ids):
                    print("Invalid Service IDs:", services_ids)
                    raise serializers.ValidationError("One or more service IDs are invalid")
                booking.services.set(services)
            except Exception as e:
                raise serializers.ValidationError(f"Error adding services: {str(e)}")

class UserBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return bookings for the logged-in user
        return Booking.objects.filter(user=self.request.user)\
                             .select_related('room')\
                             .order_by('-created_at')

class CancelBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Allow DELETE requests in addition to PUT/PATCH
    http_method_names = ['put', 'patch', 'delete']

    def delete(self, request, *args, **kwargs):
        # Fetch the booking instance
        instance = self.get_object()
        
        # Update the status to "canceled" without validation
        instance.status = 'canceled'
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        # For PUT/PATCH requests, update the status to "canceled"
        serializer.save(status='canceled')

# -------------------------------------------------
# Existing Views (Admin)
# -------------------------------------------------

class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_rooms = Room.objects.count()
        total_bookings = Booking.objects.count()
        total_customers = CustomUser.objects.count()

        return Response({
            'total_rooms': total_rooms,
            'total_bookings': total_bookings,
            'total_customers': total_customers,
        }, status=status.HTTP_200_OK)
    
class UpdateRoomView(generics.UpdateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save()

class DeleteRoomView(generics.DestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_destroy(self, instance):
        instance.delete()

class ManageCustomersView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
class AdminBookingListView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAdminUser]

class ApproveBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingStatusSerializer  # Add this line
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['patch']

    def perform_update(self, serializer):
        serializer.save(status='approved')

class RejectBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingStatusSerializer  # Add this line
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['patch']

    def perform_update(self, serializer):
        serializer.save(status='rejected')

# -------------------------------------------------
# Authentication Views (Add these)
# -------------------------------------------------
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        # Pass request context to serializer
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Get authenticated user from serializer's validated data
            user = serializer.validated_data['user']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)
        
        # Return validation errors if serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]  # Make sure you import this

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)  # partial=True allows partial updates
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                self.send_reset_email(user)
                return Response({"detail": "Password reset email sent"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"detail": "User with this email does not exist"}, 
                              status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_reset_email(self, user):
        try:
            # Generate reset token only (no uid needed)
            token = token_generator.make_token(user)

            # Prepare simplified email context
            context = {
                'user': user,
                'token': token,
            }

            # Initialize messages with fallback values
            html_message = None
            plain_message = None

            # Render text template first
            try:
                plain_message = render_to_string('registration/password_reset_email.txt', context)
                print("Text template rendered successfully")
            except Exception as e:
                print(f"Error rendering text template: {e}")
                raise

            # Attempt HTML template only if needed
            try:
                html_message = render_to_string('registration/password_reset_email.html', context)
                print("HTML template rendered successfully")
            except Exception as e:
                print(f"Error rendering HTML template: {e}")

            # Send email with fallback to text-only
            send_mail(
                "Password Reset Request",
                plain_message,
                None,
                [user.email],
                html_message=html_message,  # Safe to pass None
            )

        except Exception as e:
            print(f"Error sending email: {e}")
            return Response({"detail": "Failed to send reset email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
            
            if not token_generator.check_token(user, token):
                return Response(
                    {"detail": "Invalid or expired token"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate password strength here if needed
            user.set_password(new_password)
            user.save()
            
            # Optional: Invalidate existing user sessions
            # user.auth_token_set.all().delete()
            
            return Response(
                {"detail": "Password successfully reset"},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {"detail": "No user found with this email address"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": "Server error: {}".format(str(e))},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )