from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import datetime
from scheduler_app.validators import validate_email


class UserManager(BaseUserManager):
    def create_user(self, email, password, account_type, **kwargs):
        validate_email(email)

        email = email.lower()

        # Do not require contact info/address upon account creation
        user = self.model(email=email, account_type=account_type, **kwargs)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        return self.create_user(email, password, account_type=User.UserType.SUPERVISOR, is_staff=True,
                                is_superuser=True, is_active=True)


class User(AbstractUser):
    class UserType(models.TextChoices):
        SUPERVISOR = 'SU', 'Supervisor'
        INSTRUCTOR = 'IN', 'Instructor'
        TA = 'TA', 'TA'

    # Remove username that is inherited from AbstractUser
    username = None

    # Make email unique and set as new username for django auth
    email = models.EmailField('email', unique=True)
    USERNAME_FIELD = 'email'

    account_type = models.CharField(max_length=2, choices=UserType.choices, default=UserType.TA)
    phone_number = models.CharField(max_length=13, blank=True)
    state = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=50, blank=True)
    address_line1 = models.CharField(max_length=50, blank=True)
    address_line2 = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=9, blank=True)

    # Requiring email here will cause parsing error when opening manage.py command line.
    # Instead, handle it in manager. Password verification also does not work properly if added here
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['account_type']


class CourseManager(models.Manager):
    def create_course(self, dpt, num, **kwargs):
        name = dpt + num

        # Course names are converted to uppercase (does not affect numbers or symbols).
        name = name.upper()

        course = self.model(name=name, dpt=dpt, num=num, **kwargs)
        course.save(force_insert=True)
        return course


class Course(models.Model):
    name = models.CharField(primary_key=True, max_length=30, unique=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    term = models.CharField(max_length=20, null=True, blank=True)
    users = models.ManyToManyField(User, related_name='users-courses+')
    dpt = models.CharField(max_length=20)
    num = models.CharField(max_length=10)
    REQUIRED_FIELDS = []
    objects = CourseManager()

    def __str__(self):
        return self.name


class SectionManager(models.Manager):
    def create_section(self, section_number, course, meeting_start, meeting_end, meeting_days, **kwargs):
        if not section_number or not isinstance(section_number, str):
            raise TypeError('Section number must be provided to create a Section')

        if section_number.__len__() != 3:
            raise ValueError('Section number must be exactly 3 characters long')

        if not course or not isinstance(course, Course):
            raise TypeError('Course must be provided to create a Section')

        if not meeting_start or not isinstance(meeting_start, datetime.time):
            raise TypeError('Starting time is required to create a Section')

        if not meeting_end or not isinstance(meeting_end, datetime.time):
            raise TypeError('Ending time is required to create a Section')

        if meeting_days not in Section.MeetingDays.values:
            raise TypeError('Invalid meeting pattern')

        if meeting_start >= meeting_end:
            raise ValueError('A Section meeting cannot end until after it has started')

        try:
            section_list = Section.objects.filter(course=course)

            for rival in section_list:
                if rival.section_number == section_number:
                    raise ValueError('Two Sections with the same number cannot belong to the same Course')

        except Section.DoesNotExist:
            section_list = None

        section = self.model(section_number=section_number, course=course, meeting_start=meeting_start,
                             meeting_end=meeting_end, meeting_days=meeting_days, **kwargs)
        section.save()
        return section


class Section(models.Model):
    class SectionTypes(models.TextChoices):
        LAB = 'LAB', 'Lab'
        LECTURE = 'LEC', 'Lecture'

    class MeetingDays(models.TextChoices):
        MONDAY = 'M', 'Monday'
        TUESDAY = 'T', 'Tuesday'
        WEDNESDAY = 'W', 'Wednesday'
        THURSDAY = 'R', 'Thursday'
        FRIDAY = 'F', 'Friday'
        MON_WED = 'MW', 'Monday and Wednesday'
        TUE_THUR = 'TR', 'Tuesday and Thursday'

    section_number = models.CharField(max_length=3)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user+', on_delete=models.SET_NULL, null=True, blank=True)
    section_type = models.CharField(max_length=3, choices=SectionTypes.choices, default=SectionTypes.LECTURE)
    meeting_start = models.TimeField(null=True)
    meeting_end = models.TimeField(null=True)
    meeting_days = models.CharField(max_length=2, choices=MeetingDays.choices, default=MeetingDays.MON_WED)

    # A Section is required to have a section number, a Course, and a regular meeting schedule.
    REQUIRED_FIELDS = []

    objects = SectionManager()

    def __str__(self):
        return self.section_number

    class Meta:
        ordering = ['-section_type', 'section_number']


class SkillManager(models.Manager):
    def create_skill(self, name):
        if not name or not isinstance(name, str):
            raise TypeError('Skill name must be provided to create a Skill')

        skill = self.model(name=name)
        skill.save()
        return skill


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name='skills')

    # A Skill is required to have a name.
    REQUIRED_FIELDS = [name]

    objects = SkillManager()

    def __str__(self):
        return self.name
