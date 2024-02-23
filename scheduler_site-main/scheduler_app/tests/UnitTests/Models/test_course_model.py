from django.test import TestCase
from scheduler_app.models import Course
from django.db.utils import IntegrityError
from django.db import transaction


# These Unit Tests evaluate the Course model.
class CourseModelTest(TestCase):
    # Ensure a new Course can be created and its data is correct.
    def test_create_course(self):
        Course.objects.create_course('COMPSCI', '361')

        course_list = Course.objects.all()
        self.assertEqual(1, course_list.__len__(), msg='Incorrect number of Courses created')

        course = course_list[0]
        self.assertEqual('COMPSCI361', course.name, msg='New Course has incorrect name.')

    # Ensure a new Course can be created and its optional data is correct.
    def test_create_course_optional_arguments(self):
        Course.objects.create_course('COMPSCI', '361', description='Software Engineering', term='Spring 2022')

        course_list = Course.objects.all()
        self.assertEqual(1, course_list.__len__(), msg='Incorrect number of Courses created.')

        course = course_list[0]
        self.assertEqual('COMPSCI361', course.name, msg='New Course has incorrect name.')
        self.assertEqual('Software Engineering', course.description, msg='New Course has incorrect description.')
        self.assertEqual('Spring 2022', course.term, msg='New Course has incorrect term.')

    # Ensure the overridden __str__ method presents the Course's name.
    def test_course_to_string(self):
        Course.objects.create_course('COMPSCI', '361')

        course_list = Course.objects.all()
        course = course_list[0]
        self.assertEqual('COMPSCI361', course.__str__(), msg='New Course has incorrect string representation.')

    # Ensure a new Course will have its name converted to uppercase upon creation.
    def test_course_name_upper_case(self):
        Course.objects.create_course('compsci', '361')

        course_list = Course.objects.all()
        course = course_list[0]
        self.assertEqual('COMPSCI361', course.name, msg='New Course does not have uppercase name.')

    # Ensure a Course cannot be created with no arguments.
    def test_course_no_args(self):
        with self.assertRaises(TypeError, msg='Creating a Course with no arguments did not throw TypeError.'):
            Course.objects.create_course()

    # Ensure it is forbidden to create a second Course with the same name as the first.
    def test_create_duplicate_course_name(self):
        Course.objects.create_course('COMPSCI', '361')

        with self.assertRaises(IntegrityError, msg='Duplicate Course did not throw IntegrityError.'):
            with transaction.atomic():
                Course.objects.create_course('COMPSCI', '361')

        course_list = Course.objects.all()
        self.assertEqual(1, course_list.__len__(), msg='Incorrect number of Courses created.')

    # Ensure it is forbidden to create a second Course with the same description as the first.
    def test_create_duplicate_course_name(self):
        Course.objects.create_course('COMPSCI', '101', description='Software Engineering')

        with self.assertRaises(IntegrityError, msg='Duplicate Course did not throw IntegrityError.'):
            with transaction.atomic():
                Course.objects.create_course('COMPSCI', '101', description='Software Engineering')

        course_list = Course.objects.all()
        self.assertEqual(1, course_list.__len__(), msg='Incorrect number of Courses created.')

    # Ensure it is allowed to create three Courses in the same department but with different Course numbers.
    def test_create_course_series(self):
        Course.objects.create_course('COMPSCI', '101')
        Course.objects.create_course('COMPSCI', '102')
        Course.objects.create_course('COMPSCI', '103')

        course_list = Course.objects.all()
        self.assertEqual(3, course_list.__len__(), msg='Incorrect number of Courses created.')

        course1 = course_list[0]
        self.assertEqual('COMPSCI101', course1.name, msg='New Course 1 has incorrect name.')

        course2 = course_list[1]
        self.assertEqual('COMPSCI102', course2.name, msg='New Course 2 has incorrect name.')

        course3 = course_list[2]
        self.assertEqual('COMPSCI103', course3.name, msg='New Course 3 has incorrect name.')