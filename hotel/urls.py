from django.urls import path
from .views import (
    RoomList, 
    BookingCreate, 
    UserListView,
    UserRegistrationView,  # Add this import
    UserLoginView           # Add this import
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Authentication Endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Existing Endpoints
    path('users/', UserListView.as_view(), name='user-list'),
    path('rooms/', RoomList.as_view(), name='room-list'),
    path('bookings/', BookingCreate.as_view(), name='booking-create'),
]