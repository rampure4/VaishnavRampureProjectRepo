from django.test import Client, TestCase
from scheduler_app.models import User
from django.contrib.messages import get_messages
from django.db import IntegrityError
from django.db import transaction


# These Acceptance Tests evaluate the User's ability to create, update, and delete Users.
class AcceptanceTestUsers(TestCase):
    client = None

    def setUp(self):
        # Establish the client.
        self.client = Client()

        # Create the test Users.
        User.objects.create_user('john@uwm.edu', 'password1', User.UserType.SUPERVISOR)
        User.objects.create_user('tanya@uwm.edu', 'password1', User.UserType.INSTRUCTOR)
        User.objects.create_user('timmy@uwm.edu', 'password1', User.UserType.TA)

    # -------------------------------------------------------------------------------------------------------------
    # CRUD Tests
    # -------------------------------------------------------------------------------------------------------------

    # Ensure the initial list of Users has only one User and there are no messages.
    def test_user_list(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Go to the Users page.
        response = self.client.get('/users/', {}, follow=True)
        user_list = response.context['user_list']

        # Assert only our 3 Users exist
        self.assertEqual(3, user_list.__len__(), msg='Incorrect number of initial users.')

        # Assert no messages.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(0, messages.__len__(), msg='Incorrect number of messages.')

    # Ensure a new User can be successfully created.
    def test_add_user(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create a User.
        response = self.client.post('/add-user/',
                                    {'email': 'supervisor@uwm.edu', 'password': 'newPassword123', 'type': 'SU'},
                                    follow=True)
        user_list = response.context['user_list']

        # Assert new User created.
        self.assertEqual(4, user_list.__len__(), msg='Incorrect number of users added')
        self.assertEqual('supervisor@uwm.edu', user_list[2].email, msg='Incorrect email in User.')

        # Assert User created message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('supervisor@uwm.edu has been added.', messages, msg='Incorrect User created message.')

    # Ensure an existing User can be successfully deleted.
    def test_delete_user(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Delete a User.
        User.objects.create_user('ta@uwm.edu', 'newPassword123', User.UserType.TA)
        response = self.client.post('/delete-user/ta@uwm.edu', follow=True)
        user_list = response.context['user_list']

        # Assert only our 3 Users exist
        self.assertEqual(3, user_list.__len__(), msg='Incorrect number of Users.')

        # Assert User deleted message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('ta@uwm.edu has been deleted.', messages, msg='Incorrect User deleted message.')

    # Ensure a new User must have a valid email address.
    def test_create_user_invalid_email(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a User with an invalid email address.
        response = self.client.post('/add-user/', {'email': 'paul', 'password': 'password2', 'type': 'IN'},
                                    follow=True)
        user_list = response.context['user_list']

        # Assert invalid User was not created.
        self.assertEqual(3, user_list.__len__(), msg='User was created with invalid email.')

        # Assert invalid email address message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('paul is not a valid email.', messages,
                      msg='Incorrect invalid User creation message.')

    # Ensure a duplicate of an existing User cannot be created.
    def test_create_duplicate_user(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create a User.
        User.objects.create_user('paul@uwm.edu', 'password2', User.UserType.INSTRUCTOR)

        try:
            with transaction.atomic():
                # Attempt to create a duplicate User.
                User.objects.create_user('paul@uwm.edu', 'password2', User.UserType.INSTRUCTOR)
            self.fail('Duplicate Users are not forbidden.')
        except IntegrityError:
            pass

    # Ensure a duplicate of an existing User cannot be created even if that User has a different role.
    def test_create_duplicate_user_different_role(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create a User.
        User.objects.create_user('paul@uwm.edu', 'password2', User.UserType.INSTRUCTOR)

        try:
            with transaction.atomic():
                # Attempt to create a duplicate User with a different role.
                User.objects.create_user('paul@uwm.edu', 'password2', User.UserType.TA)
            self.fail('Duplicate Users are not forbidden even when they have different roles.')
        except IntegrityError:
            pass

    # Ensure a non-existent User cannot be deleted.
    def test_delete_nonexistent_user(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to delete a non-existent User.
        response = self.client.post('/delete-user/paul@uwm.edu', follow=True)

        # Assert User not found message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('User not found.', messages, msg='Incorrect User not found message.')

    # Ensure two different Users can have the same password (prevents hackers from spoofing passwords).
    def test_create_user_different_email_same_password(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create a User.
        User.objects.create_user('paul@uwm.edu', 'password2', User.UserType.INSTRUCTOR)

        # Create a different User with the same password.
        response = self.client.post('/add-user/', {'email': 'george@uwm.edu', 'password': 'password2', 'type': 'IN'},
                                    follow=True)
        user_list = response.context['user_list']

        # Assert new Users created.
        self.assertEqual(5, user_list.__len__(), msg='Incorrect number of Users added.')
        self.assertEqual('paul@uwm.edu', user_list[1].email, msg='First User email was incorrect.')
        self.assertEqual('george@uwm.edu', user_list[2].email, msg='Second User email was incorrect.')

        # Assert User created message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('george@uwm.edu has been added.', messages, msg='Incorrect User created message.')

    # Ensure the system is precise enough to delete exactly one specific User out of many.
    def test_create_many_users_and_delete_one(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create many Users.
        User.objects.create_user('paul@uwm.edu', 'password2', User.UserType.TA)
        User.objects.create_user('george@uwm.edu', 'password3', User.UserType.TA)
        User.objects.create_user('ringo@uwm.edu', 'password4', User.UserType.TA)
        User.objects.create_user('martin@uwm.edu', 'password5', User.UserType.TA)

        # Delete a specific User.
        response = self.client.post('/delete-user/ringo@uwm.edu', follow=True)

        # Assert User deleted.
        user_list = response.context['user_list']
        self.assertEqual(6, user_list.__len__(), msg='Incorrect number of Users.')

        # Assert User deleted message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('ringo@uwm.edu has been deleted.', messages, msg='Incorrect User deleted message.')

    # -------------------------------------------------------------------------------------------------------------
    # Logged Out Tests
    # -------------------------------------------------------------------------------------------------------------

    # Ensure a logged-out User cannot access a non-login page on the site.
    def test_users_user_logged_out(self):
        # Log in as the Supervisor and then log out.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        self.client.post('/logout_user/', follow=True)

        # Attempt to access the Users page.
        response = self.client.post('/users/', {'course_dpt': 'COMPSCI', 'course_num': '350'}, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        # Assert a redirect.
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert access denied message.
        self.assertIn('You must login to access the site.', messages, msg='Incorrect login status error message.')

    # Ensure a logged-out User cannot create a Course.
    def test_add_course_user_logged_out(self):
        # Log in as the Supervisor and then log out.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        self.client.post('/logout_user/', follow=True)

        # Attempt to create a Course.
        response = self.client.post('/add-user/', {'course_dpt': 'COMPSCI', 'course_num': '350'}, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        # Assert a redirect.
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert access denied message.
        self.assertIn('You must login to access the site.', messages, msg='Incorrect login status error message.')

    # Ensure a logged-out User cannot delete a Course.
    def test_delete_course_user_logged_out(self):
        # Log in as the Supervisor and then log out.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        self.client.post('/logout_user/', follow=True)

        # Attempt to delete a Course.
        response = self.client.post('/delete-course/COMPSCI350', follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        # Assert a redirect.
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert access denied message.
        self.assertIn('You must login to access the site.', messages, msg='Incorrect login status error message.')

    def test_logout_user(self):
        self.client.post('/', {"email": "john@uwm.edu", "password": "password1"}, follow=True)
        response = self.client.post("/logout_user/", follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)
        self.assertIn("You were logged out", messages, msg="You were logged out")

    # -------------------------------------------------------------------------------------------------------------
    # Whitespace Tests
    # -------------------------------------------------------------------------------------------------------------

    # Ensure whitespace added to the front of a User email will be removed when the User is created.
    def test_add_user_whitespace(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create a User with whitespace at the front of the User email.
        response = self.client.post('/add-user/', {'email': ' supervisor@uwm.edu ', 'password': 'newPassword123',
                                                   'type': 'SU'}, follow=True)
        user_list = response.context['user_list']

        # Assert new User created without whitespace in the email.
        self.assertEqual(4, user_list.__len__(), msg='Incorrect number of Users.')
        self.assertEqual('supervisor@uwm.edu', user_list[2].email, msg='New User email contains whitespace.')

        # Assert User created message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('supervisor@uwm.edu has been added.', messages, msg='Incorrect User created message.')

    # -------------------------------------------------------------------------------------------------------------
    # Authorization Tests
    # -------------------------------------------------------------------------------------------------------------

    # --------------------------------------------------
    # Add User
    # --------------------------------------------------

    # Ensure an Instructor cannot create a User.
    def test_add_user_instructor(self):
        # Log in as an Instructor.
        self.client.post('/', {'email': 'tanya@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a User.
        response = self.client.post('/add-user/',
                                    {'email': 'supervisor@uwm.edu', 'password': 'newPassword123', 'type': 'SU'},
                                    follow=True)

        # Assert a redirect.
        self.assertRedirects(response, '/users/', status_code=302, target_status_code=200,
                                 fetch_redirect_response=True)

        user_list = response.context['user_list']
        self.assertEqual(3, user_list.__len__(), msg='Instructor was able to add a User.')

        # Assert access denied message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denied message.')

    # Ensure a TA cannot create a User.
    def test_add_user_ta(self):
        # Log in as a TA.
        self.client.post('/', {'email': 'timmy@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a User.
        response = self.client.post('/add-user/',
                                    {'email': 'supervisor@uwm.edu', 'password': 'newPassword123', 'type': 'SU'},
                                    follow=True)

        # Assert a redirect.
        self.assertRedirects(response, '/users/', status_code=302, target_status_code=200,
                                 fetch_redirect_response=True)

        user_list = response.context['user_list']
        self.assertEqual(3, user_list.__len__(), msg='TA was able to add a User.')

        # Assert access denied message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denied message.')

    # --------------------------------------------------
    # Delete User
    # --------------------------------------------------

    # Ensure an Instructor cannot delete a User.
    def test_delete_user_instructor(self):
        # Log in as an Instructor.
        self.client.post('/', {'email': 'tanya@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a User.
        response = self.client.post('/delete-user/timmy@uwm.edu', follow=True)

        # Assert a redirect.
        self.assertRedirects(response, '/users/', status_code=302, target_status_code=200,
                                 fetch_redirect_response=True)

        user_list = response.context['user_list']
        self.assertEqual(3, user_list.__len__(), msg='Instructor was able to delete a User.')

        # Assert access denied message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denied message.')

    # Ensure a TA cannot delete a User.
    def test_delete_user_ta(self):
        # Log in as a TA.
        self.client.post('/', {'email': 'timmy@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a User.
        response = self.client.post('/delete-user/tanya@uwm.edu', follow=True)

        # Assert a redirect.
        self.assertRedirects(response, '/users/', status_code=302, target_status_code=200,
                                 fetch_redirect_response=True)

        user_list = response.context['user_list']
        self.assertEqual(3, user_list.__len__(), msg='TA was able to add a User.')

        # Assert access denied message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denied message.')
