from django.test import Client, TestCase
from scheduler_app.models import User, Course, Section
import datetime


# These Acceptance Tests evaluate the user's ability to see their schedule on the home page.
class ScheduleViewTest(TestCase):
    client = None

    wesker = None
    jill = None
    claire = None
    chris = None
    rebecca = None

    course_compsci = None
    course_opssci = None
    course_medsci = None

    days_mon_wed = None
    days_tue_thur = None
    days_wed = None
    days_thur = None
    days_fri = None

    time_9_start = None
    time_9_end = None
    time_10_start = None
    time_10_end = None
    time_1_start = None
    time_1_end = None
    time_2_start = None
    time_2_end = None

    section_compsci_201 = None
    section_compsci_202 = None
    section_compsci_901 = None
    section_compsci_902 = None

    section_opssci_101 = None
    section_opssci_102 = None
    section_opssci_801 = None
    section_opssci_802 = None

    section_medsci_301 = None
    section_medsci_302 = None
    section_medsci_601 = None
    section_medsci_602 = None

    def setUp(self):
        # Establish the client.
        self.client = Client()

        # Create the test Users.
        self.wesker = User.objects.create_user('wesker@stars.gov', 'password1', account_type=User.UserType.SUPERVISOR,
                                               first_name='Albert', last_name='Wesker')
        self.jill = User.objects.create_user('jill@stars.gov', 'password2', account_type=User.UserType.INSTRUCTOR,
                                             first_name='Jill', last_name='Valentine')
        self.claire = User.objects.create_user('claire@stars.gov', 'password3', account_type=User.UserType.INSTRUCTOR,
                                               first_name='Claire', last_name='Redfield')
        self.chris = User.objects.create_user('chris@stars.gov', 'password4', account_type=User.UserType.TA,
                                              first_name='Chris', last_name='Redfield')
        self.rebecca = User.objects.create_user('rebecca@stars.gov', 'password5', account_type=User.UserType.TA,
                                                first_name='Rebecca', last_name='Chambers')

        # Create the test Courses.
        self.course_compsci = Course.objects.create_course('COMPSCI', '361')
        self.course_opssci = Course.objects.create_course('OpsSci', '431')
        self.course_medsci = Course.objects.create_course('MEDSCI', '657')

        # Create the test meeting days.
        self.days_mon_wed = Section.MeetingDays.MON_WED
        self.days_tue_thur = Section.MeetingDays.TUE_THUR
        self.days_wed = Section.MeetingDays.WEDNESDAY
        self.days_thur = Section.MeetingDays.THURSDAY
        self.days_fri = Section.MeetingDays.FRIDAY

        # Create the test meeting times.
        self.time_9_start = datetime.time(9, 0, 0)
        self.time_9_end = datetime.time(9, 50, 0)
        self.time_10_start = datetime.time(10, 0, 0)
        self.time_10_end = datetime.time(10, 50, 0)
        self.time_1_start = datetime.time(13, 0, 0)
        self.time_1_end = datetime.time(13, 50, 0)
        self.time_2_start = datetime.time(14, 0, 0)
        self.time_2_end = datetime.time(14, 50, 0)

        # Create the test Sections.
        self.section_compsci_201 = Section.objects.create_section('201', self.course_compsci, self.time_9_start,
                                                                  self.time_9_end, self.days_mon_wed,
                                                                  user=self.jill)
        self.section_compsci_202 = Section.objects.create_section('202', self.course_compsci, self.time_10_start,
                                                                  self.time_10_end, self.days_mon_wed,
                                                                  user=self.jill)
        self.section_compsci_901 = Section.objects.create_section('901', self.course_compsci, self.time_1_start,
                                                                  self.time_1_end, self.days_wed, user=self.chris)
        self.section_compsci_902 = Section.objects.create_section('902', self.course_compsci, self.time_2_start,
                                                                  self.time_2_end, self.days_wed, user=self.chris)

        self.section_opssci_101 = Section.objects.create_section('101', self.course_opssci, self.time_1_start,
                                                                 self.time_1_end, self.days_mon_wed,
                                                                 user=self.jill)
        self.section_opssci_102 = Section.objects.create_section('102', self.course_opssci, self.time_2_start,
                                                                 self.time_2_end, self.days_mon_wed,
                                                                 user=self.jill)
        self.section_opssci_801 = Section.objects.create_section('801', self.course_opssci, self.time_1_start,
                                                                 self.time_1_end, self.days_fri, user=self.chris)
        self.section_opssci_802 = Section.objects.create_section('802', self.course_opssci, self.time_2_start,
                                                                 self.time_2_end, self.days_fri, user=self.chris)

        self.section_medsci_301 = Section.objects.create_section('301', self.course_medsci, self.time_9_start,
                                                                 self.time_9_end, self.days_tue_thur,
                                                                 user=self.jill)
        self.section_medsci_302 = Section.objects.create_section('302', self.course_medsci, self.time_10_start,
                                                                 self.time_10_end, self.days_tue_thur,
                                                                 user=self.jill)
        self.section_medsci_601 = Section.objects.create_section('601', self.course_medsci, self.time_1_start,
                                                                 self.time_1_end, self.days_thur, user=self.chris)
        self.section_medsci_602 = Section.objects.create_section('602', self.course_medsci, self.time_2_start,
                                                                 self.time_2_end, self.days_thur, user=self.chris)

    # Ensure a Supervisor will see an empty schedule.
    def test_schedule_normal_supervisor(self):
        self.client.post('/', {'email': 'wesker@stars.gov', 'password': 'password1'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        username = response.context['first_name']
        assignments_list = response.context['assignments_list']

        self.assertEqual('Albert', username, msg='Supervisor was not greeted by name.')
        self.assertFalse(assignments_list, msg='Supervisor does not have an empty schedule.')

    # Ensure an Instructor will see all of his/her assignments in the schedule.
    def test_schedule_normal_instructor(self):
        self.client.post('/', {'email': 'jill@stars.gov', 'password': 'password2'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        username = response.context['first_name']
        assignments_list = response.context['assignments_list']

        self.assertEqual('Jill', username, msg='Instructor was not greeted by name.')

        monday_list = assignments_list['Monday']
        tuesday_list = assignments_list['Tuesday']
        wednesday_list = assignments_list['Wednesday']
        thursday_list = assignments_list['Thursday']

        self.assertEqual(4, monday_list.__len__(), msg='Instructor had wrong number of Sections on Monday.')
        self.assertEqual(self.section_compsci_201.pk, monday_list[0].pk,
                         msg='Instructors first Monday Section was wrong.')
        self.assertEqual(self.section_compsci_202.pk, monday_list[1].pk,
                         msg='Instructors second Monday Section was wrong.')
        self.assertEqual(self.section_opssci_101.pk, monday_list[2].pk,
                         msg='Instructors third Monday Section was wrong.')
        self.assertEqual(self.section_opssci_102.pk, monday_list[3].pk,
                         msg='Instructors fourth Monday Section was wrong.')

        self.assertEqual(2, tuesday_list.__len__(), msg='Instructor had wrong number of Sections on Tuesday.')
        self.assertEqual(self.section_medsci_301.pk, tuesday_list[0].pk,
                         msg='Instructors first Tuesday Section was wrong.')
        self.assertEqual(self.section_medsci_302.pk, tuesday_list[1].pk,
                         msg='Instructors second Tuesday Section was wrong.')

        self.assertEqual(4, wednesday_list.__len__(), msg='Instructor had wrong number of Sections on Wednesday.')
        self.assertEqual(self.section_compsci_201.pk, wednesday_list[0].pk,
                         msg='Instructors first Wednesday Section was wrong.')
        self.assertEqual(self.section_compsci_202.pk, wednesday_list[1].pk,
                         msg='Instructors second Wednesday Section was wrong.')
        self.assertEqual(self.section_opssci_101.pk, wednesday_list[2].pk,
                         msg='Instructors third Wednesday Section was wrong.')
        self.assertEqual(self.section_opssci_102.pk, wednesday_list[3].pk,
                         msg='Instructors fourth Wednesday Section was wrong.')

        self.assertEqual(2, thursday_list.__len__(), msg='Instructor had wrong number of Sections on Thursday.')
        self.assertEqual(self.section_medsci_301.pk, thursday_list[0].pk,
                         msg='Instructors first Thursday Section was wrong.')
        self.assertEqual(self.section_medsci_302.pk, thursday_list[1].pk,
                         msg='Instructors second Thursday Section was wrong.')

    # Ensure a TA will see all of his/her assignments in the schedule.
    def test_schedule_normal_ta(self):
        self.client.post('/', {'email': 'chris@stars.gov', 'password': 'password4'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        username = response.context['first_name']
        assignments_list = response.context['assignments_list']

        self.assertEqual('Chris', username, msg='TA was not greeted by name.')

        wednesday_list = assignments_list['Wednesday']
        thursday_list = assignments_list['Thursday']
        friday_list = assignments_list['Friday']

        self.assertEqual(2, wednesday_list.__len__(), msg='TA had wrong number of Sections on Wednesday.')
        self.assertEqual(self.section_compsci_901.pk, wednesday_list[0].pk,
                         msg='TAs first Wednesday Section was wrong.')
        self.assertEqual(self.section_compsci_902.pk, wednesday_list[1].pk,
                         msg='TAs second Wednesday Section was wrong.')

        self.assertEqual(2, thursday_list.__len__(), msg='TA had wrong number of Sections on Thursday.')
        self.assertEqual(self.section_medsci_601.pk, thursday_list[0].pk, msg='TAs first Thursday Section was wrong.')
        self.assertEqual(self.section_medsci_602.pk, thursday_list[1].pk, msg='TAs second Thursday Section was wrong.')

        self.assertEqual(2, friday_list.__len__(), msg='TA had wrong number of Sections on Friday.')
        self.assertEqual(self.section_opssci_801.pk, friday_list[0].pk, msg='TAs first Friday Section was wrong.')
        self.assertEqual(self.section_opssci_802.pk, friday_list[1].pk, msg='TAs second Friday Section was wrong.')

    # Ensure an Instructor will not see assignments that he/she has not been assigned to.
    def test_schedule_no_overlap_instructor(self):
        self.client.post('/', {'email': 'jill@stars.gov', 'password': 'password2'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        assignments_list = response.context['assignments_list']

        wednesday_list = assignments_list['Wednesday']
        thursday_list = assignments_list['Thursday']

        self.assertNotIn(self.section_compsci_901, wednesday_list, msg='Instructor is seeing a TA assignment.')
        self.assertNotIn(self.section_compsci_902, wednesday_list, msg='Instructor is seeing a TA assignment.')

        self.assertNotIn(self.section_medsci_601, thursday_list, msg='Instructor is seeing a TA assignment.')
        self.assertNotIn(self.section_medsci_602, thursday_list, msg='Instructor is seeing a TA assignment.')

    # Ensure a TA will not see assignments that he/she has not been assigned to.
    def test_schedule_no_overlap_ta(self):
        self.client.post('/', {'email': 'chris@stars.gov', 'password': 'password4'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        assignments_list = response.context['assignments_list']

        monday_list = assignments_list['Monday']
        wednesday_list = assignments_list['Wednesday']
        thursday_list = assignments_list['Thursday']

        self.assertNotIn(self.section_opssci_101, monday_list, msg='TA is seeing an Instructor assignment.')
        self.assertNotIn(self.section_opssci_102, monday_list, msg='TA is seeing an Instructor assignment.')

        self.assertNotIn(self.section_opssci_101, wednesday_list, msg='TA is seeing an Instructor assignment.')
        self.assertNotIn(self.section_opssci_102, wednesday_list, msg='TA is seeing an Instructor assignment.')

        self.assertNotIn(self.section_medsci_301, thursday_list, msg='TA is seeing an Instructor assignment.')
        self.assertNotIn(self.section_medsci_302, thursday_list, msg='TA is seeing an Instructor assignment.')

    # Ensure an Instructor will not see an entry for a day that he/she does not work.
    def test_schedule_off_days_instructor(self):
        self.client.post('/', {'email': 'jill@stars.gov', 'password': 'password2'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        assignments_list = response.context['assignments_list']

        self.assertFalse(assignments_list['Friday'], msg='Instructor had an entry for a day with no assignments.')

    # Ensure a TA will not see an entry for a day that he/she does not work.
    def test_schedule_off_days_ta(self):
        self.client.post('/', {'email': 'chris@stars.gov', 'password': 'password4'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        assignments_list = response.context['assignments_list']

        self.assertFalse(assignments_list['Tuesday'], msg='TA had an entry for a day with no assignments.')

    # Ensure an Instructor who has no assignments will see an empty schedule.
    def test_schedule_slacker_instructor(self):
        self.client.post('/', {'email': 'claire@stars.gov', 'password': 'password3'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        username = response.context['first_name']
        assignments_list = response.context['assignments_list']

        self.assertEqual('Claire', username, msg='Slacker Instructor was not greeted by name.')

        self.assertFalse(assignments_list, msg='Slacker instructor does not have an empty schedule.')

    # Ensure a TA who has no assignments will see an empty schedule.
    def test_schedule_slacker_ta(self):
        self.client.post('/', {'email': 'rebecca@stars.gov', 'password': 'password5'}, follow=True)
        response = self.client.get('/home/', {}, follow=True)
        username = response.context['first_name']
        assignments_list = response.context['assignments_list']

        self.assertEqual('Rebecca', username, msg='Slacker TA was not greeted by name.')

        self.assertFalse(assignments_list, msg='Slacker TA does not have an empty schedule.')
