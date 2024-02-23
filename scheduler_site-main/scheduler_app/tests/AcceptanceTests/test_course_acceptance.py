from django.test import Client, TransactionTestCase
from scheduler_app.models import User, Course, Section
from django.contrib.messages import get_messages


# These Acceptance Tests evaluate the user's ability to create, update, and delete Courses.
class AcceptanceTestCourses(TransactionTestCase):
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

    # Ensure the initial list of Courses is empty and there are no messages.
    def test_initial_course_list(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Go to the Course page.
        response = self.client.get('/courses/', {}, follow=True)
        course_list = response.context['course_list']

        # Assert empty Course list.
        self.assertEqual(0, course_list.__len__(), msg='Incorrect number of initial Courses.')

        # Assert no messages.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(0, messages.__len__(), msg='Incorrect number of messages.')

    # Ensure a new Course can be successfully created.
    def test_create_course(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create a Course.
        response = self.client.post('/add-course/',
                                    {'course_dpt': 'COMPSCI', 'course_num': '361', 'course_descr': 'Hard class'},
                                    follow=True)
        course_list = response.context['course_list']

        # Assert new Course created.
        self.assertEqual(1, course_list.__len__(), msg='Incorrect number of Courses added.')
        self.assertEqual('COMPSCI361', course_list[0].name, msg='Incorrect new Course name.')
        self.assertEqual('Hard class', course_list[0].description, msg='Incorrect new Course description.')

        # Assert Course created message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI361 has been added.', messages, msg='Incorrect Course created message.')

    # Ensure an existing Course can be successfully deleted.
    def test_delete_course(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Delete a Course.
        course = Course.objects.create_course('COMPSCI', '361')
        response = self.client.post('/delete-course/%s' % course.name, follow=True)
        course_list = response.context['course_list']

        # Assert empty Course list.
        self.assertEqual(0, course_list.__len__(), msg='Course was not deleted.')

        # Assert Course deleted message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('%s has been deleted.' % course.name, messages, msg='Incorrect Course deleted message.')

    # Ensure a duplicate of an existing Course cannot be created.
    def test_create_duplicate_course(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a duplicate Course.
        self.client.post('/add-course/', {'course_dpt': 'COMPSCI', 'course_num': '361', 'course_descr': ''},
                         follow=True)
        response = self.client.post('/add-course/', {'course_dpt': 'COMPSCI', 'course_num': '361', 'course_descr': ''},
                                    follow=True)

        # Assert Course already exists message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI361 already exists.', messages,
                      msg='Incorrect Course already exists message.')

    # Ensure a nonexistent Course cannot be deleted.
    def test_delete_nonexistent_course(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to delete a nonexistent Course.
        response = self.client.post('/delete-course/BIO102', follow=True)

        # Assert Course not found message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Course not found.', messages, msg='Incorrect Course not found message.')

    # Ensure a Course with an invalid name cannot be created.
    def test_invalid_course_name(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a Course with an invalid name.
        response = self.client.post('/add-course/', {'course_dpt': '361', 'course_num': '361'}, follow=True)

        # Assert invalid Course name message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Requested course name is invalid.', messages, msg='Incorrect invalid Course name message.')

    # Ensure a Course with an invalid number cannot be created.
    def test_invalid_course_number(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a Course with an invalid number.
        response = self.client.post('/add-course/', {'course_dpt': 'COMPSCI', 'course_num': 'COMPSCI'}, follow=True)

        # Assert invalid Course number message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Requested course name is invalid.', messages, msg='Incorrect invalid Course name message.')

    # Ensure it is allowed to create two Courses with the same name but different numbers.
    def test_create_course_same_name_different_number(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create two Courses with the same name but different numbers.
        self.client.post('/add-course/', {'course_dpt': 'COMPSCI', 'course_num': '101', 'course_descr': ''},
                         follow=True)
        response = self.client.post('/add-course/', {'course_dpt': 'COMPSCI', 'course_num': '102', 'course_descr': ''},
                                    follow=True)
        course_list = response.context['course_list']

        # Assert two Courses in the Course list.
        self.assertEqual(2, course_list.__len__(), msg='Incorrect number of Courses added.')

        # Assert Courses have correct names.
        self.assertEqual('COMPSCI101', course_list[0].name, msg='Incorrect first Course name.')
        self.assertEqual('COMPSCI102', course_list[1].name, msg='Incorrect second Course name.')

        # Assert Course created message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI102 has been added.', messages, msg='Incorrect Course created message.')

    # Ensure it is allowed to create two Courses with different names but the same numbers.
    def test_create_course_different_name_same_number(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create two Courses with different names but the same numbers.
        self.client.post('/add-course/', {'course_dpt': 'ENGL', 'course_num': '101', 'course_descr': ''}, follow=True)
        response = self.client.post('/add-course/', {'course_dpt': 'MEDSCI', 'course_num': '101', 'course_descr': ''},
                                    follow=True)
        course_list = response.context['course_list']

        # Assert two Courses in the Course list.
        self.assertEqual(2, course_list.__len__(), msg='Incorrect number of Courses added.')

        # Assert Course have correct names.
        self.assertEqual('ENGL101', course_list[0].name, msg='Incorrect first Course name.')
        self.assertEqual('MEDSCI101', course_list[1].name, msg='Incorrect second Course name.')

        # Assert Course created message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('MEDSCI101 has been added.', messages, msg='Incorrect Course created message.')

    # Ensure the system is precise enough to delete exactly one specific Course out of many.
    def test_create_many_courses_and_delete_one(self):
        # Create many Courses.
        Course.objects.create_course('COMPSCI', '101')
        Course.objects.create_course('COMPSCI', '102')
        Course.objects.create_course('COMPSCI', '103')
        Course.objects.create_course('COMPSCI', '104')
        Course.objects.create_course('COMPSCI', '105')
        Course.objects.create_course('COMPSCI', '106')
        Course.objects.create_course('COMPSCI', '107')
        Course.objects.create_course('COMPSCI', '108')
        deleted = Course.objects.create_course('COMPSCI', '109')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Delete a specific Course.
        response = self.client.post('/delete-course/%s' % deleted.name, follow=True)

        # Assert Course deleted message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('%s has been deleted.' % deleted.name, messages, msg='Incorrect Course deleted message.')

        # Assert correct number of Courses in Course list.
        course_list = response.context['course_list']
        self.assertEqual(8, course_list.__len__(), msg='Incorrect number of Courses in the Course list.')

        # Verify correct Course was deleted.
        self.assertNotIn(deleted, course_list, msg='Deleted Course was still present.')

    # Ensure a Course can have its fields updated.
    def test_update_course(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Java class')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section, User, and new description.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'add_user': 'john@uwm.edu',
                                        'section_type': 'LEC',
                                        'section_number': '901',
                                        'section_start': '11:00',
                                        'section_end': '11:50',
                                        'section_days': 'MW'
                                    },
                                    follow=True)
        course = response.context['course_list'][0]

        # Assert Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')

        # Verify new description.
        self.assertEqual('Data structures in Java', course.description, msg='Incorrect description in the Course.')

        # Verify User was added to the Course.
        self.assertEqual(1, course.users.all().count())
        self.assertEqual('john@uwm.edu', course.users.all()[0].email)

        # Verify a Section was added.
        sections = Section.objects.all()
        self.assertEqual(1, sections.__len__())

        # Verify data of new Section.
        section = sections[0]
        self.assertEqual('LEC', section.section_type, msg='Section type is incorrect')
        self.assertEqual('901', section.section_number, msg='Section number is incorrect')
        self.assertEqual(11, section.meeting_start.hour, msg='Section meeting start hour is incorrect')
        self.assertEqual(0, section.meeting_start.minute, msg='Section meeting start minute is incorrect')
        self.assertEqual(11, section.meeting_end.hour, msg='Section meeting end hour is incorrect')
        self.assertEqual(50, section.meeting_end.minute, msg='Section meeting end minute is incorrect')
        self.assertEqual('MW', section.meeting_days, msg='Section meeting days is incorrect')
        self.assertEqual('COMPSCI350', section.course.name, msg='Section Course name is incorrect')

        # Update again and remove the Course and User.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Another one',
                                        'remove_user': 'john@uwm.edu',
                                        'remove_section': '901',
                                    },
                                    follow=True)

        course = response.context['course_list'][0]

        # Assert Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')

        # Verify new description.
        self.assertEqual('Another one', course.description, msg='Incorrect description in the Course.')

        # Verify User was removed from the Course.
        self.assertEqual(0, course.users.all().count(), msg='Incorrect number of Users in the Course.')

        # Verify the Section was deleted from the database.
        sections = Section.objects.all()
        self.assertEqual(0, sections.__len__(), msg='Incorrect number of Sections in the database.')

    # -------------------------------------------------------------------------------------------------------------
    # Advanced Update Tests
    # -------------------------------------------------------------------------------------------------------------

    # Ensure a Course can be updated with an invalid Section and still receive the valid parts of its update.
    def test_update_invalid_section(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Java class')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Leave out a field for a new Section when updating the Course.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'add_user': 'john@uwm.edu',
                                        'section_type': 'LEC',
                                        'section_start': '11:00',
                                        'section_end': '11:50',
                                        'section_days': 'MW'
                                    },
                                    follow=True)
        course = response.context['course_list'][0]

        # Assert invalid Section message and Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(2, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Invalid section request', messages, msg='Incorrect unsuccessful Course update message.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')

        # Verify new description was saved.
        self.assertEqual('Data structures in Java', course.description, msg='Incorrect description in the Course')

        # Verify User was still added to the Course.
        self.assertEqual(1, course.users.all().count(), msg='Incorrect number of Users in the Course')
        self.assertEqual('john@uwm.edu', course.users.all()[0].email, msg='Incorrect User added to the Course.')

        # Verify no Section was added.
        sections = Section.objects.all()
        self.assertEqual(0, sections.__len__(), msg='Incorrect number of Sections in the Course.')

    # Ensure a Course can be updated with an invalid Section number and still receive the valid parts of its update.
    def test_update_duplicate_section_number(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Java class')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section, User, and new description.
        self.client.post('/update-course/COMPSCI350',
                         {
                             'course_descr': 'Data structures in Java',
                             'add_user': 'john@uwm.edu',
                             'section_type': 'LEC',
                             'section_number': '901',
                             'section_start': '11:00',
                             'section_end': '11:50',
                             'section_days': 'MW'
                         },
                         follow=True)

        # Update Course with another Section with the same number as the first.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'add_user': 'john@uwm.edu',
                                        'section_type': 'LAB',
                                        'section_number': '901',
                                        'section_start': '9:00',
                                        'section_end': '10:00',
                                        'section_days': 'TR'
                                    },
                                    follow=True)
        course = response.context['course_list'][0]

        # Assert invalid Section message and Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(2, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Two Sections with the same number cannot belong to the same Course', messages,
                      msg='Incorrect unsuccessful Course update message.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')

        # Verify new description.
        self.assertEqual('Data structures in Java', course.description, msg='Incorrect description in the Course.')

        # Verify User was added to the Course.
        self.assertEqual(1, course.users.all().count(), msg='Incorrect number of Users in the Course')
        self.assertEqual('john@uwm.edu', course.users.all()[0].email, msg='Incorrect User added to the Course.')

        # Verify the duplicate Section was not added.
        sections = Section.objects.all()
        self.assertEqual(1, sections.__len__(), msg='Incorrect number of Sections in the Course.')

    # Ensure a Course can be updated with an invalid Section time and still receive the valid parts of its update.
    def test_update_invalid_section_times(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Java class')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section, User, and new description.
        # Set the start time after the end time to create an invalid time.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'add_user': 'john@uwm.edu',
                                        'section_type': 'LEC',
                                        'section_number': '901',
                                        'section_start': '11:50',
                                        'section_end': '11:00',
                                        'section_days': 'MW'
                                    },
                                    follow=True)
        course = response.context['course_list'][0]

        # Assert invalid Section message and Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(2, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('A Section meeting cannot end until after it has started', messages,
                      msg='Incorrect unsuccessful Course update message.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message')

        # Verify new description.
        self.assertEqual('Data structures in Java', course.description, msg='Incorrect description in the Course.')

        # Verify User was added to the course.
        self.assertEqual(1, course.users.all().count(), msg='Incorrect number of Users in the Course.')
        self.assertEqual('john@uwm.edu', course.users.all()[0].email, msg='Incorrect User added to the Course.')

        # Verify the invalid Section was not added.
        sections = Section.objects.all()
        self.assertEqual(0, sections.__len__(), msg='Incorrect number of Sections in the Course.')

    # Ensure a Course can be updated so a User can be added to one of its Sections.
    def test_update_add_user_to_section(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Data structures in Java')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section and User.
        self.client.post('/update-course/COMPSCI350',
                         {
                             'course_descr': 'Data structures in Java',
                             'add_user': 'tanya@uwm.edu',
                             'section_type': 'LEC',
                             'section_number': '901',
                             'section_start': '11:00',
                             'section_end': '11:50',
                             'section_days': 'MW'
                         },
                         follow=True)

        # Assign User to Section
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'to_sec_num': '901',
                                        'to_sec_user': 'tanya@uwm.edu'
                                    },
                                    follow=True)

        # Assert Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')

        # Verify User was added to the Section.
        section = Section.objects.all()[0]
        self.assertEqual('tanya@uwm.edu', section.user.email, msg='User was not added to the Section.')

    # Ensure a Course cannot have its Section updated with an unspecified User.
    def test_update_invalid_section_request(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Data structures in Java')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section.
        self.client.post('/update-course/COMPSCI350',
                         {
                             'course_descr': 'Data structures in Java',
                             'section_type': 'LEC',
                             'section_number': '901',
                             'section_start': '11:00',
                             'section_end': '11:50',
                             'section_days': 'MW'
                         },
                         follow=True)

        # Assign User to Section without specifying User.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'to_sec_num': '901',
                                    },
                                    follow=True)

        # Assert invalid User assignment message and Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(2, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')
        self.assertIn('When assigning user to a section, user must be specified.', messages,
                      msg='Incorrect User cannot be assigned message.')

    # Ensure a User cannot be assigned to a Section that is being removed.
    def test_update_add_user_to_removed_section(self):
        # Create a course.
        Course.objects.create_course('COMPSCI', '350', description='Data structures in Java')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section and User.
        self.client.post('/update-course/COMPSCI350',
                         {
                             'course_descr': 'Data structures in Java',
                             'add_user': 'tanya@uwm.edu',
                             'section_type': 'LEC',
                             'section_number': '901',
                             'section_start': '11:00',
                             'section_end': '11:50',
                             'section_days': 'MW'
                         },
                         follow=True)

        # Assign User to Section while also removing Section.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'remove_section': '901',
                                        'to_sec_num': '901',
                                        'to_sec_user': 'tanya@uwm.edu'
                                    },
                                    follow=True)

        # Assert invalid User assignment message and Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(2, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')
        self.assertIn('Cannot assign user to a section that is being removed.', messages,
                      msg='Incorrect User cannot be assigned message.')

        # Verify Section was still deleted.
        self.assertEqual(0, Section.objects.all().__len__(), msg='Section was not deleted')

    # Ensure a User cannot be assigned to a Section if that User is being removed.
    def test_update_add_removed_user(self):
        # Create a course.
        Course.objects.create_course('COMPSCI', '350', description='Data structures in Java')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section and User.
        self.client.post('/update-course/COMPSCI350',
                         {
                             'course_descr': 'Data structures in Java',
                             'add_user': 'tanya@uwm.edu',
                             'section_type': 'LEC',
                             'section_number': '901',
                             'section_start': '11:00',
                             'section_end': '11:50',
                             'section_days': 'MW'
                         },
                         follow=True)

        # Assign User to Section while also removing that User.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'remove_user': 'tanya@uwm.edu',
                                        'to_sec_num': '901',
                                        'to_sec_user': 'tanya@uwm.edu'
                                    },
                                    follow=True)

        # Assert invalid User assignment message and Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(2, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')
        self.assertIn('Cannot assign a user to a section if they are being removed from the course.', messages,
                      msg='Incorrect invalid User assignment message.')

        # Verify User was not added to the Section.
        section = Section.objects.all()[0]
        self.assertEqual(None, section.user)

    # Ensure only Instructors can be assigned to lecture Sections.
    def test_update_add_non_instructor_to_lecture(self):
        # Create a course.
        Course.objects.create_course('COMPSCI', '350', description='Data structures in Java')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section and User.
        self.client.post('/update-course/COMPSCI350',
                         {
                             'course_descr': 'Data structures in Java',
                             'add_user': 'john@uwm.edu',
                             'section_type': 'LEC',
                             'section_number': '901',
                             'section_start': '11:00',
                             'section_end': '11:50',
                             'section_days': 'MW'
                         },
                         follow=True)

        # Assign User to Section.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'to_sec_num': '901',
                                        'to_sec_user': 'john@uwm.edu'
                                    },
                                    follow=True)

        # Assert invalid User assignment message and Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(2, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')
        self.assertIn('Only instructors can be assigned to lectures.', messages,
                      msg='Incorrect invalid User assignment message.')

        # Verify User was not added to the Section.
        section = Section.objects.all()[0]
        self.assertEqual(None, section.user, msg='User was added to the Section.')

    # Ensure only Users that are assigned to a Course can be assigned to one of that Course's Sections.
    def test_update_add_invalid_user_to_section(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Data structures in Java')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Update Course with Section.
        self.client.post('/update-course/COMPSCI350',
                         {
                             'course_descr': 'Data structures in Java',
                             'section_type': 'LEC',
                             'section_number': '901',
                             'section_start': '11:00',
                             'section_end': '11:50',
                             'section_days': 'MW'
                         },
                         follow=True)

        # Assign User to Section.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'to_sec_num': '901',
                                        'to_sec_user': 'john@uwm.edu'
                                    },
                                    follow=True)

        # Assert invalid User assignment message and Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(2, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')
        self.assertIn('A user must belong to a course to be assigned to a section of the course.', messages,
                      msg='Incorrect invalid User assignment message.')

        # Verify User was not added to the Section.
        section = Section.objects.all()[0]
        self.assertEqual(None, section.user, msg='User was added to the Section.')

    # -------------------------------------------------------------------------------------------------------------
    # Logged Out Tests
    # -------------------------------------------------------------------------------------------------------------

    # Ensure a logged-out User cannot access the Course page.
    def test_courses_user_logged_out(self):
        # Log in as the Supervisor and then log out.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        self.client.post('/logout_user/', follow=True)

        # Attempt to access the Course page.
        response = self.client.post('/courses/', {'course_dpt': 'COMPSCI', 'course_num': '350'}, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        # Assert a redirect.
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert login status error message.
        self.assertIn('You must login to access the site.', messages, msg='Incorrect login status error message.')

    # Ensure a logged-out User cannot add a Course.
    def test_add_course_user_logged_out(self):
        # Log in as the Supervisor and then log out.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        self.client.post('/logout_user/', follow=True)

        # Attempt to add a Courses.
        response = self.client.post('/add-course/', {'course_dpt': 'COMPSCI', 'course_num': '350'}, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        # Assert a redirect.
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert login status error message.
        self.assertIn('You must login to access the site.', messages, msg='Incorrect login status error message.')

    # Ensure a logged-out User cannot delete Courses.
    def test_delete_course_user_logged_out(self):
        # Log in as the Supervisor and then log out.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        self.client.post('/logout_user/', follow=True)

        # Attempt to delete a Course.
        response = self.client.post('/delete-course/1', {'course_dpt': 'COMPSCI', 'course_num': '350'}, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        # Assert a redirect.
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert login status error message.
        self.assertIn('You must login to access the site.', messages, msg='Incorrect login status error message.')

    # Ensure a logged-out User cannot update Courses.
    def test_update_course_user_logged_out(self):
        # Log in as the Supervisor and then log out.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)
        self.client.post('/logout_user/', follow=True)

        # Attempt to update a Course.
        # TODO - Just like deletes, we need a better way to get the course id instead of passing in the literal
        response = self.client.post('/update-course/1', {'course_dpt': 'COMPSCI', 'course_num': '350'}, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]

        # Assert a redirect.
        self.assertRedirects(response, '/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert login status error message.
        self.assertIn('You must login to access the site.', messages, msg='Incorrect login status error message.')

    # -------------------------------------------------------------------------------------------------------------
    # Whitespace Tests
    # -------------------------------------------------------------------------------------------------------------

    # Ensure whitespace added to the front of a Course name will be removed when the Course is created.
    def test_add_course_whitespace(self):
        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Create a Course with whitespace at the front of the Course name.
        response = self.client.post('/add-course/', {'course_dpt': ' COMPSCI ', 'course_num': ' 350 ',
                                                     'course_descr': 'A science class'}, follow=True)
        course_list = response.context['course_list']

        # Assert new Course created without whitespace in the name.
        self.assertEqual(1, course_list.__len__(), msg='Incorrect number of Courses added.')
        self.assertEqual('COMPSCI350', course_list[0].name, msg='New Course name contains whitespace.')

        # Assert Course created message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been added.', messages, msg='Incorrect Course creation message.')

    # -------------------------------------------------------------------------------------------------------------
    # Authorization Tests
    # -------------------------------------------------------------------------------------------------------------

    # --------------------------------------------------
    # Add Course
    # --------------------------------------------------

    # Ensure an Instructor cannot create a Course.
    def test_add_course_instructor(self):
        # Log in as an Instructor.
        self.client.post('/', {'email': 'tanya@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a Course.
        response = self.client.post('/add-course/',
                                    {'course_dpt': 'COMPSCI', 'course_num': '350', 'course_descr': 'A science class'},
                                    follow=True)

        # Assert a redirect.
        self.assertRedirects(response, '/courses/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert empty Course list.
        course_list = response.context['course_list']
        self.assertEqual(0, course_list.__len__(), msg='Instructor was able to add a Course.')

        # Assert access denied message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denied message.')

    # Ensure a TA cannot create a Course.
    def test_add_course_ta(self):
        # Log in as a TA.
        self.client.post('/', {'email': 'timmy@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to create a Course.
        response = self.client.post('/add-course/',
                                    {'course_dpt': 'COMPSCI', 'course_num': '350', 'course_descr': 'A science class'},
                                    follow=True)

        # Assert a redirect.
        self.assertRedirects(response, '/courses/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert empty Course list.
        course_list = response.context['course_list']
        self.assertEqual(0, course_list.__len__(), msg='TA was able to add a Course.')

        # Assert access denied message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denied message.')

    # --------------------------------------------------
    # Delete Course
    # --------------------------------------------------

    # Ensure an Instructor cannot delete a Course.
    def test_delete_course_instructor(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350')

        # Log in as an Instructor.
        self.client.post('/', {'email': 'tanya@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to delete a Course
        response = self.client.post('/delete-course/COMPSCI350', follow=True)

        # Assert a redirect.
        self.assertRedirects(response, '/courses/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        # Assert Course was not deleted.
        course_list = response.context['course_list']
        self.assertEqual(1, course_list.__len__(), msg='Incorrect number of Courses in Course list.')

        # Assert access denied message,
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denies message.')

    # Ensure a TA cannot delete a Course.
    def test_delete_course_ta(self):
        # Create course
        Course.objects.create_course('COMPSCI', '350')

        # Log in as ta
        self.client.post('/', {'email': 'timmy@uwm.edu', 'password': 'password1'}, follow=True)

        response = self.client.post('/delete-course/COMPSCI350', follow=True)

        self.assertRedirects(response, '/courses/', status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

        course_list = response.context['course_list']
        self.assertEqual(1, course_list.__len__(), msg='TA was able to delete a Course.')

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denies message.')

    # --------------------------------------------------
    # Update Course
    # --------------------------------------------------

    # Ensure Instructors are able to update Courses they are assigned to.
    def test_update_course_instructor_valid(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Java class')

        # Log in as the Supervisor.
        self.client.post('/', {'email': 'john@uwm.edu', 'password': 'password1'}, follow=True)

        # Assign Instructor to the Course an add a Section.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'add_user': 'tanya@uwm.edu',
                                        'section_type': 'LEC',
                                        'section_number': '901',
                                        'section_start': '11:00',
                                        'section_end': '11:50',
                                        'section_days': 'MW'
                                    },
                                    follow=True)

        # Log out.
        self.client.post('/logout/', follow=True)

        # Log in as an Instructor.
        self.client.post('/', {'email': 'tanya@uwm.edu', 'password': 'password1'}, follow=True)

        # Assign self to the Section.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'to_sec_num': '901',
                                        'to_sec_user': 'tanya@uwm.edu'
                                    },
                                    follow=True)

        # Assert Course updated message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('COMPSCI350 has been updated.', messages, msg='Incorrect Course updated message.')

        # Verify User was added to the Section.
        section = Section.objects.all()[0]
        self.assertEqual('tanya@uwm.edu', section.user.email, msg='Incorrect User added to Section.')

    # Ensure Instructors cannot update Courses they are not assigned to.
    def test_update_course_instructor_invalid(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Java class')

        # Log in as an Instructor.
        self.client.post('/', {'email': 'tanya@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to update a Course that this Instructor is not assigned to.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'add_user': 'john@uwm.edu',
                                        'section_type': 'LEC',
                                        'section_number': '901',
                                        'section_start': '11:00',
                                        'section_end': '11:50',
                                        'section_days': 'MW'
                                    },
                                    follow=True)

        # Assert access denied message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denied message.')

        course = response.context['course_list'][0]

        # Verify description was not changed.
        self.assertEqual('Java class', course.description, msg='Incorrect description in the Course.')

        # Verify User was not added to the Course.
        self.assertEqual(0, course.users.all().count(), msg='Incorrect number of Users in the Course.')

        # Verify a Section was not added.
        sections = Section.objects.all()
        self.assertEqual(0, sections.__len__(), msg='Incorrect number of Sections in the Course.')

    # Ensure TAs cannot update Courses.
    def test_update_course_ta(self):
        # Create a Course.
        Course.objects.create_course('COMPSCI', '350', description='Java class')

        # Log in as a TA.
        self.client.post('/', {'email': 'timmy@uwm.edu', 'password': 'password1'}, follow=True)

        # Attempt to update a Course.
        response = self.client.post('/update-course/COMPSCI350',
                                    {
                                        'course_descr': 'Data structures in Java',
                                        'add_user': 'john@uwm.edu',
                                        'section_type': 'LEC',
                                        'section_number': '901',
                                        'section_start': '11:00',
                                        'section_end': '11:50',
                                        'section_days': 'MW'
                                    },
                                    follow=True)

        # Assert access denied message.
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, messages.__len__(), msg='Incorrect number of messages.')
        self.assertIn('Access denied.', messages, msg='Incorrect access denies message.')

        course = response.context['course_list'][0]

        # Verify description was not changed.
        self.assertEqual('Java class', course.description, msg='Incorrect description in the Course.')

        # Verify User was not added to the Course.
        self.assertEqual(0, course.users.all().count(), msg='Incorrect number of Users in the Course.')

        # Verify a Section was not added.
        sections = Section.objects.all()
        self.assertEqual(0, sections.__len__(), msg='Incorrect number of Sections in the Course.')
