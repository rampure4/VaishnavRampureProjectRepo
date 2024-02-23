import re
from django.core.exceptions import ValidationError

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def validate_email(email):
    if not re.fullmatch(regex, email):
        raise ValidationError(
            '%(email)s is not a valid email address',
            params={'email': email}
        )
