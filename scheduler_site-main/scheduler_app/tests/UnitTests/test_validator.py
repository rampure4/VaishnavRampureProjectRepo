from django.test import TestCase
from scheduler_app.validators import validate_email
from django.core.exceptions import ValidationError


class ValidatorTest(TestCase):

    def test_validate_email_valid(self):
        email = "testemail@test.com"
        try:
            validate_email(email)
        except ValidationError:
            self.fail("Valid email raised ValidationError")

    def test_validate_email_invalid(self):
        email = "testemail"

        with self.assertRaises(ValidationError, msg='Invalid email did not raise ValidationError'):
            validate_email(email)
