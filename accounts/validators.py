import re
from django.core.exceptions import ValidationError

email_re = re.compile(r"^[\w.+-]+@([\w-]+\.)+[\w-]{2,}$")

def validate_email(value):
    if not email_re.match(value):
        raise ValidationError('Enter a valid email address.')

def validate_password_complexity(value):
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', value):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', value):
        raise ValidationError('Password must contain at least one digit.')
