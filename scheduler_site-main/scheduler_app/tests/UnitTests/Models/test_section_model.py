from django.test import TestCase
from scheduler_app.models import User, Course, Section
from django.db import transaction
import datetime


# These Unit Tests evaluate the Section model.
class SectionModelTest(TestCase):
    course = None
    meeting_start = None
    meeting_end = None
    meeting_days = None
    instructor = None
    ta = None
    invalid = None

    def setUp(self):
        # Create the test Section.
        self.course = Course.objects.create_course('COMPSCI', '361')
        self.meeting_start = datetime.time(10, 0, 0)
        self.meeting_end = datetime.time(11, 0, 0)
        self.meeting_days = Section.MeetingDays.MON_WED
        self.instructor = User.objects.create_user('john@uwm.edu', 'password1', account_type=User.UserType.INSTRUCTOR)
        self.ta = User.objects.create_user('paul@uwm.edu', 'password2', account_type=User.UserType.TA)
        self.invalid = User.objects.create_user('invalid@domain.com', 'invalid', account_type=User.UserType.TA)

    # Ensure a new Section can be created and its data is correct.
    def test_create_section(self):
        Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_end, self.meeting_days)

        section_list = Section.objects.all()
        self.assertEqual(1, section_list.__len__(), msg='Incorrect number of Sections created.')

        section = section_list[0]
        self.assertEqual('201', section.section_number, msg='New Section has incorrect Section number.')
        self.assertEqual(section.course.pk, self.course.pk, msg='New Section has incorrect Course.')
        self.assertEqual(section.meeting_start, self.meeting_start, msg='New Section has incorrect meeting start.')
        self.assertEqual(section.meeting_end, self.meeting_end, msg='New Section has incorrect meeting end.')
        self.assertEqual(section.meeting_days, self.meeting_days, msg='New Section has incorrect meeting days.')

    # Ensure a new Section can be created and its optional data is correct.
    def test_create_section_optional_arguments(self):
        Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_end, self.meeting_days,
                                       user=self.instructor)

        section_list = Section.objects.all()
        self.assertEqual(1, section_list.__len__(), msg='Incorrect number of Sections created.')

        section = section_list[0]
        self.assertEqual('201', section.section_number, msg='New Section has incorrect Section number.')
        self.assertEqual(section.course.pk, self.course.pk, msg='New Section has incorrect Course.')
        self.assertEqual(section.meeting_start, self.meeting_start, msg='New Section has incorrect meeting start.')
        self.assertEqual(section.meeting_end, self.meeting_end, msg='New Section has incorrect meeting end.')
        self.assertEqual(section.meeting_days, self.meeting_days, msg='New Section has incorrect meeting days.')
        self.assertEqual(section.user, self.instructor, msg='New Section has incorrect Instructor.')

    # Ensure the overridden __str__ method presents the Section's Section number.
    def test_section_to_string(self):
        Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_end, self.meeting_days)

        section_list = Section.objects.all()
        section = section_list[0]
        self.assertEqual('201', section.__str__(), msg='New Section has incorrect string representation.')

    # Ensure a Section cannot be created with no arguments.
    def test_section_no_args(self):
        with self.assertRaises(TypeError, msg='Creating a Section with no arguments did not throw TypeError.'):
            Section.objects.create_section()

    # Ensure a Section cannot be created with no Section number.
    def test_section_no_number(self):
        with self.assertRaises(TypeError, msg='Creating a Section with no Section number did not throw a TypeError.'):
            Section.objects.create_section(None, self.course, self.meeting_start, self.meeting_end, self.meeting_days)

    # Ensure a Section cannot be created with an invalid Section number.
    def test_section_invalid_number(self):
        with self.assertRaises(ValueError,
                               msg='Creating a Section with an invalid Section number did not throw a TypeError.'):
            Section.objects.create_section('1234', self.course, self.meeting_start, self.meeting_end, self.meeting_days)

    # Ensure a Section cannot be created with no Course.
    def test_section_no_course(self):
        with self.assertRaises(TypeError, msg='Creating a Section with no Course did not throw a TypeError.'):
            Section.objects.create_section('201', None, self.meeting_start, self.meeting_end, self.meeting_days)

    # Ensure a Section cannot be created with an invalid Course.
    def test_section_invalid_course(self):
        with self.assertRaises(TypeError, msg='Creating a Section with an invalid Course did not throw a TypeError.'):
            Section.objects.create_section('201', self.invalid, self.meeting_start, self.meeting_end, self.meeting_days)

    # Ensure a Section cannot be created with no meeting start.
    def test_section_no_meeting_start(self):
        with self.assertRaises(TypeError, msg='Creating a Section with no meeting start did not throw a TypeError.'):
            Section.objects.create_section('201', self.course, None, self.meeting_end, self.meeting_days)

    # Ensure a Section cannot be created with an invalid meeting start.
    def test_section_invalid_meeting_start(self):
        with self.assertRaises(TypeError,
                               msg='Creating a Section with an invalid meeting start did not throw a TypeError.'):
            Section.objects.create_section('201', self.course, self.invalid, self.meeting_end, self.meeting_days)

    # Ensure a Section cannot be created with no meeting end.
    def test_section_no_meeting_end(self):
        with self.assertRaises(TypeError, msg='Creating a Section with no meeting end did not throw a TypeError.'):
            Section.objects.create_section('201', self.course, self.meeting_start, None, self.meeting_days)

    # Ensure a Section cannot be created with an invalid meeting end.
    def test_section_invalid_meeting_end(self):
        with self.assertRaises(TypeError,
                               msg='Creating a Section with an invalid meeting end did not throw a TypeError.'):
            Section.objects.create_section('201', self.course, self.meeting_start, self.invalid, self.meeting_days)

    # Ensure a Section cannot be created with no meeting days.
    def test_section_no_meeting_days(self):
        with self.assertRaises(TypeError, msg='Creating a Section with no meeting days did not throw a TypeError.'):
            Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_end, None)

    # Ensure a Section cannot be created with invalid meeting days.
    def test_section_invalid_meeting_days(self):
        with self.assertRaises(TypeError,
                               msg='Creating a Section with an invalid meeting end did not throw a TypeError.'):
            Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_end, self.invalid)

    # Ensure it is forbidden to create a Section with the same section number as another Section in the same Course.
    def test_create_duplicate_section(self):
        Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_end, self.meeting_days)

        with self.assertRaises(ValueError, msg='Duplicate Section did not throw ValueError.'):
            with transaction.atomic():
                Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_end,
                                               self.meeting_days)

        section_list = Section.objects.all()
        self.assertEqual(1, section_list.__len__(), msg='Incorrect number of Sections created.')

    # Ensure it is allowed to create a Section with the same section number as another Section in a different Course.
    def test_create_separate_sections_same_number(self):
        courseA = Course.objects.create_course('COMPSCI', '101')
        courseB = Course.objects.create_course('COMPSCI', '102')

        Section.objects.create_section('201', courseA, self.meeting_start, self.meeting_end, self.meeting_days)
        Section.objects.create_section('201', courseB, self.meeting_start, self.meeting_end, self.meeting_days)

        section_list = Section.objects.all()
        self.assertEqual(2, section_list.__len__(), msg='Incorrect number of Sections created.')

    # Ensure it is allowed for two Sections in the same Course to meet at the same time (supports hybrid classes).
    def test_create_simultaneous_sections(self):
        Section.objects.create_section('101', self.course, self.meeting_start, self.meeting_end, self.meeting_days)
        Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_end, self.meeting_days)

        section_list = Section.objects.all()
        self.assertEqual(2, section_list.__len__(), msg='Incorrect number of Sections created.')

    # Ensure it is forbidden for a Section to end before it starts.
    def test_section_ends_before_starts(self):
        with self.assertRaises(ValueError, msg='Section that ends before it starts did not throw ValueError.'):
            with transaction.atomic():
                Section.objects.create_section('201', self.course, self.meeting_end, self.meeting_start,
                                               self.meeting_days)

        section_list = Section.objects.all()
        self.assertEqual(0, section_list.__len__(), msg='Incorrect number of Sections created.')

    # Ensure it is forbidden for a Section to end at the same time it starts.
    def test_section_ends_and_starts_at_same_time(self):
        with self.assertRaises(ValueError, msg='Section that ends at the time it starts did not throw ValueError.'):
            with transaction.atomic():
                Section.objects.create_section('201', self.course, self.meeting_start, self.meeting_start,
                                               self.meeting_days)

        section_list = Section.objects.all()
        self.assertEqual(0, section_list.__len__(), msg='Incorrect number of Sections created.')

    # Ensure it is allowed to create three Sections in the same Course but with different section numbers.
    def test_create_section_series(self):
        Section.objects.create_section('101', self.course, self.meeting_start, self.meeting_end, self.meeting_days)
        Section.objects.create_section('102', self.course, self.meeting_start, self.meeting_end, self.meeting_days)
        Section.objects.create_section('103', self.course, self.meeting_start, self.meeting_end, self.meeting_days)

        section_list = Section.objects.all()
        self.assertEqual(3, section_list.__len__(), msg='Incorrect number of Sections created.')

        sectionA = section_list[0]
        self.assertEqual('101', sectionA.section_number, msg='First Section has incorrect section number.')
        self.assertEqual(sectionA.course.pk, self.course.pk, msg='First Section has incorrect course.')
        self.assertEqual(sectionA.meeting_start, self.meeting_start, msg='First Section has incorrect meeting start.')
        self.assertEqual(sectionA.meeting_end, self.meeting_end, msg='First Section has incorrect meeting end.')
        self.assertEqual(sectionA.meeting_days, self.meeting_days, msg='First Section has incorrect meeting days.')

        sectionB = section_list[1]
        self.assertEqual('102', sectionB.section_number, msg='Second Section has incorrect section number.')
        self.assertEqual(sectionB.course.pk, self.course.pk, msg='Second Section has incorrect course.')
        self.assertEqual(sectionB.meeting_start, self.meeting_start, msg='Second Section has incorrect meeting start.')
        self.assertEqual(sectionB.meeting_end, self.meeting_end, msg='Second Section has incorrect meeting end.')
        self.assertEqual(sectionB.meeting_days, self.meeting_days, msg='Second Section has incorrect meeting days.')

        sectionC = section_list[2]
        self.assertEqual('103', sectionC.section_number, msg='Third Section has incorrect section number.')
        self.assertEqual(sectionC.course.pk, self.course.pk, msg='Third Section has incorrect course.')
        self.assertEqual(sectionC.meeting_start, self.meeting_start, msg='Third Section has incorrect meeting start.')
        self.assertEqual(sectionC.meeting_end, self.meeting_end, msg='Third Section has incorrect meeting end.')
        self.assertEqual(sectionC.meeting_days, self.meeting_days, msg='Third Section has incorrect meeting days.')
