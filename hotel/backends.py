from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Get the first user with this email (temporary fix)
            user = UserModel.objects.filter(email=email).first()
        except UserModel.DoesNotExist:
            return None
        
        if user and user.check_password(password):
            return user
        return None