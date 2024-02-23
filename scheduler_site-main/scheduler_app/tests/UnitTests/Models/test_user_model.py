from django.test import TestCase
from scheduler_app.models import User
from django.db.utils import IntegrityError
from django.db import transaction
from django.core.exceptions import ValidationError


# These Unit Tests evaluate the User model.
class UserModelTest(TestCase):
    # Ensure a new User can be created and its data is correct.
    def test_create_user(self):
        User.objects.create_user('jDoe123@uwm.edu',
                                 'test_password123',
                                 User.UserType.SUPERVISOR,
                                 first_name='John',
                                 last_name='Doe',
                                 phone_number='(414)555-5555',
                                 state='WI',
                                 city='Milwaukee',
                                 address_line1='123 W. Hampton',
                                 address_line2='Apt 3',
                                 zipcode='57984')

        # Verify a single new User was created and verify its data
        user_list = User.objects.all()
        self.assertEqual(1, user_list.__len__(), msg='Incorrect number of Users created.')

        user = user_list[0]
        self.assertEqual('jdoe123@uwm.edu', user.email, msg='New user has incorrect username.')
        self.assertTrue(user.password, msg='New users password missing.')
        self.assertEqual('John', user.first_name, msg='New user has incorrect first name.')
        self.assertEqual('Doe', user.last_name, msg='New user has incorrect last name.')
        self.assertEqual(User.UserType.SUPERVISOR, user.account_type, msg='New user has incorrect account type.')
        self.assertEqual('(414)555-5555', user.phone_number, msg='New user has incorrect phone number.')
        self.assertEqual('WI', user.state, msg='New user has incorrect state.')
        self.assertEqual('Milwaukee', user.city, msg='New user has incorrect city.')
        self.assertEqual('123 W. Hampton', user.address_line1, msg='New user has incorrect address line 1.')
        self.assertEqual('Apt 3', user.address_line2, msg='New user has incorrect address line 2.')
        self.assertEqual('57984', user.zipcode, msg='New user has incorrect zipcode.')

    # Ensure it is forbidden to create a User with the same email address as another User.
    def test_create_user_duplicate_email(self):
        User.objects.create_user('jdoe123@uwm.edu', 'test_password01', User.UserType.SUPERVISOR)

        with self.assertRaises(IntegrityError, msg='Duplicate email did not throw IntegrityError.'):
            with transaction.atomic():
                User.objects.create_user('jdoe123@uwm.edu', 'test_password01', User.UserType.TA)

        # Verify only one User exists.
        user_list = User.objects.all()
        self.assertEqual(1, user_list.__len__(), msg='Incorrect number of Users created.')

    # Ensure it is forbidden to create a User with an invalid email address.
    def test_create_user_invalid_email(self):

        with self.assertRaises(ValidationError, msg='Invalid email did not throw ValidationError'):
            User.objects.create_user('john', 'test_password01', User.UserType.SUPERVISOR)

        # Verify no User was created.
        user_list = User.objects.all()
        self.assertEqual(0, user_list.__len__(), msg='Incorrect number of Users created.')
