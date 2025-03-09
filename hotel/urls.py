from django.urls import path
from .views import (
    RoomList,
    BookingCreateView,
    UserBookingListView,
    UserRegistrationView,
    UserLoginView,
    BookingCreateView,
    UserBookingListView,
    CancelBookingView,
    AdminBookingListView,
    ApproveBookingView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Authentication Endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Booking endpoints
    path('bookings/create/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/my-bookings/', UserBookingListView.as_view(), name='user-bookings'),
    path('bookings/cancel/<int:pk>/', CancelBookingView.as_view(), name='cancel-booking'),

    # Admin Booking endpoints
    path('admin/bookings/', AdminBookingListView.as_view(), name='admin-bookings'),
    path('admin/bookings/approve/<int:pk>/', ApproveBookingView.as_view(), name='approve-booking'),

    # Existing Endpoints
    path('users/', UserBookingListView.as_view(), name='user-list'),
    path('rooms/', RoomList.as_view(), name='room-list'),
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
]