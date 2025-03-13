from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Room, Booking, CustomUser
from .serializers import (
    RoomSerializer, 
    BookingSerializer, 
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# -------------------------------------------------
# Existing Views (Rooms, Bookings, Users)
# -------------------------------------------------
class RoomList(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can create rooms

class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Get room ID from request data
        room_id = self.request.data.get('room')
        room = Room.objects.get(id=room_id)
        
        serializer.save(
            user=self.request.user,
            room=room
        )

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

    def perform_update(self, serializer):
        # Allow users to cancel their own bookings
        serializer.save(status='canceled')

# -------------------------------------------------
# Existing Views (Admin)
# -------------------------------------------------
class AdminBookingListView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAdminUser]

class ApproveBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save(status='approved')

class RejectBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save(status='canceled')

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