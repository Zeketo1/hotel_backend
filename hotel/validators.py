from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import os

def validate_image_url(value):
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(urlparse(value).path)[1]
    
    if not ext.lower() in allowed_extensions:
        raise ValidationError(
            f'Unsupported file extension: {ext}. Allowed: {", ".join(allowed_extensions)}'
        )