from django.test import Client, TestCase
from scheduler_app.models import User
from django.contrib.messages import get_messages


# These Acceptance Tests evaluate the user's ability to log in to the application.
class AcceptanceTestLogin(TestCase):
    client = None
    email_list = None
    password_list = None

    def setUp(self):
        # Establish the client.
        self.client = Client()

        # Define the lists of User email addresses and passwords.
        self.email_list = ['john@uwm.edu', 'paul@uwm.edu', 'george@uwm.edu', 'ringo@uwm.edu']
        self.password_list = ['password1', 'password2', 'password3', 'password4']

        # Store test Users in the testing database.
        for i in range(len(self.email_list)):
            temp_user = User.objects.create_user(self.email_list[i], self.password_list[i], User.UserType.INSTRUCTOR)
            temp_user.save()

    # Ensure a User can log in successfully with the correct credentials and be directed to the home page.
    def test_login_user_success(self):

        for i in range(len(self.email_list)):
            response = self.client.post('/', {'email': self.email_list[i], 'password': self.password_list[i]},
                                        follow=True)
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertRedirects(response, '/home/', status_code=302, target_status_code=200,
                                 fetch_redirect_response=True)
            self.assertEqual(0, messages.__len__(), msg='Incorrect number of mesages.')

    # Ensure a User who is logged in will be able to see the home page.
    def test_login_already_logged_in(self):
        response = self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual('/home/', response.request['PATH_INFO'], msg='Incorrect page.')
        self.assertEqual(0, messages.__len__(), msg='Incorrect number of messages.')

        response = self.client.get('/', follow=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual('/home/', response.request['PATH_INFO'], msg='Incorrect page.')
        self.assertEqual(0, messages.__len__(), msg='Incorrect number of messages.')

    # Ensure a User cannot log in with an invalid email address and will be given an error message.
    def test_login_user_invalid_email(self):

        for i in range(len(self.email_list)):
            response = self.client.post('/', {'email': 'invalid_email', 'password': self.password_list[i]}, follow=True)
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual('/', response.request['PATH_INFO'], msg='Incorrect page.')
            self.assertIn('Email or password is invalid.', messages,
                          msg='Incorrect login error message for invalid email.')

    # Ensure a User cannot log in with an invalid password and will be given an error message.
    def test_login_user_invalid_password(self):

        for i in range(len(self.email_list)):
            response = self.client.post('/', {'email': self.email_list[i], 'password': 'invalid_password'}, follow=True)
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual('/', response.request['PATH_INFO'], msg='Incorrect page.')
            self.assertIn('Email or password is invalid.', messages,
                          msg='Incorrect login error message for invalid password.')

    # Ensure a User cannot log in with no email address and will be given an error message.
    def test_login_user_no_email(self):

        for i in range(len(self.email_list)):
            response = self.client.post('/', {'password': self.password_list[i]}, follow=True)
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual('/', response.request['PATH_INFO'], msg='Incorrect page.')
            self.assertIn('Email or password is invalid.', messages, msg='Incorrect login error message for no email.')

    # Ensure a User cannot log in with no password and will be given an error message.
    def test_login_user_no_password(self):

        for i in range(len(self.email_list)):
            response = self.client.post('/', {'email': self.email_list[i]}, follow=True)
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual('/', response.request['PATH_INFO'], msg='Incorrect page.')
            self.assertIn('Email or password is invalid.', messages,
                          msg='Incorrect login error message for no password.')

    # Ensure a User cannot log in with another User's password
    # (assuming it is not also their own password) and an error message is given.
    def test_user_login_stolen_password(self):

        for i in range(2, 5):
            response = self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password' + i.__str__()},
                                        follow=True)
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual('/', response.request['PATH_INFO'], msg='Incorrect page.')
            self.assertIn('Email or password is invalid.', messages,
                          msg='Incorrect login error message for stolen password.')

    # Ensure a new User can be registered with the same password as another User
    # and can log in successfully to the home page.
    # Allowing several Users to have the same password without knowing
    # will prevent hackers from spoofing passwords from registered Users.
    def test_user_login_duplicate_password(self):

        new_user = User.objects.create_user('martin@uwm.edu', 'password1', User.UserType.TA)
        new_user.save()

        response = self.client.post('/', {'email': 'martin@uwm.edu', 'password': 'password1'}, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertRedirects(response, '/home/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)
        self.assertEqual(0, messages.__len__(), msg='Incorrect number of messages.')
