from django.test import Client, TestCase
from scheduler_app.models import User, Skill
from django.contrib.messages import get_messages


# These Acceptance Tests evaluate the user's ability to see edit user info.
class UserInfoViewTest(TestCase):
    client = None

    def setUp(self):
        # Establish the client.
        self.client = Client()

        # Create the test Users.
        User.objects.create_user('john@uwm.edu', 'password1', User.UserType.SUPERVISOR)
        User.objects.create_user('ashley@uwm.edu', 'password1', User.UserType.INSTRUCTOR)
        User.objects.create_user('timmy@uwm.edu', 'password1', User.UserType.TA)

    # Ensure the User will be redirected to the home page after editing one's own User info.
    def test_user_info_success(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update your User info.
        response = self.client.post('/user-info/john@uwm.edu', {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-555-5555',
            'city': 'Milwaukee',
            'state': 'WI',
            'addr_1': '123 Street Rd.',
            'addr_2': 'Apt. 6',
            'zipcode': '53214',
        })

        # Saving your own contact info should redirect you to home page.
        self.assertRedirects(response, '/home/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Account info updated.', messages, msg='Account info update message not present.')

        # Verify data was saved.
        user = User.objects.filter(email='john@uwm.edu')[0]
        self.assertEqual('John', user.first_name)
        self.assertEqual('Doe', user.last_name)
        self.assertEqual('555-555-5555', user.phone_number)
        self.assertEqual('Milwaukee', user.city)
        self.assertEqual('WI', user.state)
        self.assertEqual('123 Street Rd.', user.address_line1)
        self.assertEqual('Apt. 6', user.address_line2)
        self.assertEqual('53214', user.zipcode)

    # Ensure the Supervisor will be redirected to the Users page after editing some other User's info.
    def test_user_info_of_other_redirects(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update other User's info.
        response = self.client.post('/user-info/ashley@uwm.edu', {
            'first_name': 'Ashley',
            'last_name': 'Doe',
            'phone': '111-222-3333',
            'city': 'Milwaukee',
            'state': 'WI',
            'addr_1': '321 Road St.',
            'addr_2': 'Apt. 2',
            'zipcode': '53221',
        })

        # Saving contact info of someone else should redirect you to Users page.
        self.assertRedirects(response, '/users/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Account info updated.', messages, msg='Account info update message not present.')

        # Verify data was saved.
        user = User.objects.filter(email='ashley@uwm.edu')[0]
        self.assertEqual('Ashley', user.first_name)
        self.assertEqual('Doe', user.last_name)
        self.assertEqual('111-222-3333', user.phone_number)
        self.assertEqual('Milwaukee', user.city)
        self.assertEqual('WI', user.state)
        self.assertEqual('321 Road St.', user.address_line1)
        self.assertEqual('Apt. 2', user.address_line2)
        self.assertEqual('53221', user.zipcode)

    # Ensure instructors cannot access/edit the info of others
    def test_user_info_instructor(self):
        # Log in as an instructor.
        self.client.post('/', {'email': 'ashley@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to update User info.
        response = self.client.post('/user-info/john@uwm.edu', {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-555-5555',
            'city': 'Milwaukee',
            'state': 'WI',
            'addr_1': '123 Street Rd.',
            'addr_2': 'Apt. 6',
            'zipcode': '53214',
        })

        # Access denied should redirect to home page.
        self.assertRedirects(response, '/home/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Access denied.', messages, msg='Access denial message not present.')

        # Attempt to access User info.
        response = self.client.get('/user-info/john@uwm.edu')

        # Access denied should redirect to home page.
        self.assertRedirects(response, '/home/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Access denied.', messages, msg='Access denial message not present.')

    # Ensure TAs cannot access/edit the info of others
    def test_user_info_ta(self):
        # Log in as a TA.
        self.client.post('/', {'email': 'timmy@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to update User info.
        response = self.client.post('/user-info/john@uwm.edu', {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-555-5555',
            'city': 'Milwaukee',
            'state': 'WI',
            'addr_1': '123 Street Rd.',
            'addr_2': 'Apt. 6',
            'zipcode': '53214',
        })

        # Access denied should redirect to home page.
        self.assertRedirects(response, '/home/', status_code=302, target_status_code=200,
                                fetch_redirect_response=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Access denied.', messages, msg='Access denial message not present.')

        # Attempt to access User info.
        response = self.client.get('/user-info/john@uwm.edu')

        # Access denied should redirect to home page.
        self.assertRedirects(response, '/home/', status_code=302, target_status_code=200,
                                fetch_redirect_response=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Access denied.', messages, msg='Access denial message not present.')

    # Ensure a nonexistent User cannot have info updated.
    def test_user_info_not_found(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to access info of a User who does not exist.
        response = self.client.get('/user-info/notreal@uwm.edu')

        # Invalid User should redirect to users page with message.
        self.assertRedirects(response, '/users/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('User not found.', messages, msg='Invalid user info message incorrect.')

        # Attempt to update info of User who does not exist.
        response = self.client.post('/user-info/notreal@uwm.edu', {
            'first_name': 'Fake',
            'last_name': 'User',
            'phone': '555-555-5555',
            'city': 'Milwaukee',
            'state': 'WI',
            'addr_1': '123 Street Rd.',
            'addr_2': 'Apt. 6',
            'zipcode': '53214',
        })

        # Invalid User should redirect to users page with message.
        self.assertRedirects(response, '/users/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('User not found.', messages, msg='Account info update message not present.')

    # Ensure a logged-out User cannot edit User info.
    def test_user_info_logged_out(self):
        # Log in as the Supervisor then log out.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        self.client.post('/logout_user/', follow=True)

        # Attempt to access User info.
        response = self.client.post('/user-info/john@uwm.edu', follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        # Assert a redirect.
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert access denied message.
        self.assertIn('You must login to access the site.', messages, msg='Login status error message not present.')

    def test_user_info_add_skill(self):
        skill = Skill.objects.create_skill("Leadership")

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update your User info to add the Skill.
        response = self.client.post('/user-info/john@uwm.edu', {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-555-5555',
            'city': 'Milwaukee',
            'state': 'WI',
            'addr_1': '123 Street Rd.',
            'addr_2': 'Apt. 6',
            'zipcode': '53214',
            'skill-add': skill
        })

        # Assert the Skill was saved.
        user = User.objects.filter(email='john@uwm.edu')[0]
        self.assertEqual(user, skill.users.all()[0], msg='Skill was not assigned to the User.')


    def test_user_info_remove_skill(self):
        skill = Skill.objects.create_skill("Leadership")

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update your User info to add the Skill.
        response = self.client.post('/user-info/john@uwm.edu', {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-555-5555',
            'city': 'Milwaukee',
            'state': 'WI',
            'addr_1': '123 Street Rd.',
            'addr_2': 'Apt. 6',
            'zipcode': '53214',
            'skill-add': skill
        })

        # Assert the Skill was added.
        user = User.objects.filter(email='john@uwm.edu')[0]
        self.assertIn(user, skill.users.all(), msg='Skill was not assigned to the User.')

        # Update your User info to remove the Skill.
        response = self.client.post('/user-info/john@uwm.edu', {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-555-5555',
            'city': 'Milwaukee',
            'state': 'WI',
            'addr_1': '123 Street Rd.',
            'addr_2': 'Apt. 6',
            'zipcode': '53214',
            'skill-remove': skill
        })

        # Assert the Skill was removed.
        user = User.objects.filter(email='john@uwm.edu')[0]
        self.assertNotIn(user, skill.users.all(), msg='Skill was not assigned to the User.')