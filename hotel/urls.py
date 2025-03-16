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
    RejectBookingView,
    UserProfileView,
    AdminDashboardView,
    RoomDetailView,
    UpdateRoomView,
    DeleteRoomView,
    PasswordResetView, 
    PasswordResetConfirmView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
     # JWT Token Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Authentication Endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('auth/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # User Booking endpoints
    path('bookings/create/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/my-bookings/', UserBookingListView.as_view(), name='user-bookings'),
    path('bookings/cancel/<int:pk>/', CancelBookingView.as_view(), name='cancel-booking'),

    # Admin Booking endpoints
    path('admin/bookings/', AdminBookingListView.as_view(), name='admin-bookings'),
    path('admin/bookings/approve/<int:pk>/', ApproveBookingView.as_view(), name='approve-booking'),
    path('admin/bookings/reject/<int:pk>/', RejectBookingView.as_view(), name='reject-booking'),
    # Admin Dashboard
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),

    # Existing Endpoints
    path('user/', UserProfileView.as_view(), name='user-profile'),
    path('users/', UserBookingListView.as_view(), name='user-list'),
    path('rooms/', RoomList.as_view(), name='room-list'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('rooms/update/<int:pk>/', UpdateRoomView.as_view(), name='update-room'),
    path('rooms/delete/<int:pk>/', DeleteRoomView.as_view(), name='delete-room'),
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
]