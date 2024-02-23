from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import IntegrityError
from datetime import datetime
from django.db.models import Q
from operator import attrgetter

from scheduler_app.models import Course, User, Section, Skill
from django.core.exceptions import ValidationError, ObjectDoesNotExist


def login_page(request):
    # check for post request
    if request.method == 'POST':

        # Emails are stored in lowercase, so we make request email lowercase to make this
        # case-insensitive
        email = request.POST.get('email')

        if email is not None:
            email = email.lower()
        else:
            email = ""

        password = request.POST.get('password')

        # authenticate user
        user = authenticate(request, email=email, password=password)

        # if user is in database login and redirect to home if not reload page with error
        if user is not None:
            login(request, user)
            return redirect('scheduler-home')
        else:
            messages.error(request, 'Email or password is invalid.')
            return redirect('scheduler-login')

    if request.user.is_authenticated:
        return redirect("scheduler-home")

    # else a GET request, simply render page
    return render(request, 'scheduler_app/login.html')


def home_page(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    if request.user.account_type == User.UserType.SUPERVISOR:
        # Pass the user's first name and empty list of assignments into the template.
        context = {
            'first_name': request.user.first_name,
            'assignments_list': None,
        }
    else:
        # Get the sections this user is assigned to organized by day.
        section_list = Section.objects.filter(user=request.user)

        if section_list.__len__() == 0:
            # Pass the user's first name and empty assignments list into the template.
            context = {
                'first_name': request.user.first_name,
                'assignments_list': None,
                'user': request.user
            }
        else:
            section_list = sorted(section_list, key=attrgetter('meeting_start'))

            monday_list = [section for section in section_list if (section.meeting_days == Section.MeetingDays.MONDAY) | (
                    section.meeting_days == Section.MeetingDays.MON_WED)]

            tuesday_list = [section for section in section_list if (section.meeting_days == Section.MeetingDays.TUESDAY) | (
                    section.meeting_days == Section.MeetingDays.TUE_THUR)]

            wednesday_list = [section for section in section_list if
                              (section.meeting_days == Section.MeetingDays.WEDNESDAY) | (
                                      section.meeting_days == Section.MeetingDays.MON_WED)]

            thursday_list = [section for section in section_list if
                             (section.meeting_days == Section.MeetingDays.THURSDAY) | (
                                     section.meeting_days == Section.MeetingDays.TUE_THUR)]

            friday_list = [section for section in section_list if section.meeting_days == Section.MeetingDays.FRIDAY]

            # Compile all section assignments into a dictionary corresponding to which day the section occurs during.
            assignments_list = {'Monday': monday_list, 'Tuesday': tuesday_list, 'Wednesday': wednesday_list,
                                'Thursday': thursday_list, 'Friday': friday_list}

            # Pass the user's first name and section assignments into the template.
            context = {
                'first_name': request.user.first_name,
                'assignments_list': assignments_list,
                'user': request.user,
                'current_day': datetime.today().strftime('%A')
            }

    return render(request, 'scheduler_app/home.html', context)


def course_page(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    if request.method == 'GET':
        course_list = Course.objects.order_by('dpt', 'num')
        return render(request, "scheduler_app/courses.html", {"course_list": course_list, 'user': request.user})


def add_course(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    # Get current user
    user = User.objects.filter(email=request.user.email)[0]

    # Supervisor only action
    if user.account_type != User.UserType.SUPERVISOR:
        messages.warning(request, "Access denied.")
        return redirect('scheduler-courses')

    if request.method == 'POST':
        dpt = ''
        num = ''
        try:
            dpt = request.POST['course_dpt'].strip()
            if not dpt.isalpha():
                raise ValueError

            num = request.POST['course_num'].strip()
            if not num.isdigit():
                raise ValueError

            description = request.POST['course_descr']
            course = Course.objects.create_course(dpt=dpt, num=num, description=description)
            messages.success(request, course.name + " has been added.")
            return redirect('scheduler-courses')
        except ValueError:
            messages.warning(request, "Requested course name is invalid.")
            return render(request, 'scheduler_app/add-course.html')
        except IntegrityError:
            messages.warning(request, dpt + num + " already exists.")
            return redirect('scheduler-courses')
    else:
        return render(request, 'scheduler_app/add-course.html')


def delete_course(request, name):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    # Get current user
    user = User.objects.filter(email=request.user.email)[0]

    # Supervisor only action
    if user.account_type != User.UserType.SUPERVISOR:
        messages.warning(request, "Access denied.")
        return redirect('scheduler-courses')

    try:
        course = Course.objects.get(name=name)
        course.delete()
        messages.success(request, name + " has been deleted.")
        return redirect('scheduler-courses')
    except ObjectDoesNotExist:
        messages.warning(request, 'Course not found.')
        return redirect('scheduler-courses')


def update_course(request, name):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    try:
        course = Course.objects.get(name=name)
    except ObjectDoesNotExist:
        messages.warning(request, 'Course not found.')
        return redirect('scheduler-courses')

    # Get current user
    user = User.objects.filter(email=request.user.email)[0]

    # Supervisor/instructor only
    if user.account_type == User.UserType.TA:
        messages.warning(request, "Access denied.")
        return redirect('scheduler-courses')

    # Instructor must belong to course in order to edit it
    if user.account_type == User.UserType.INSTRUCTOR and user not in course.users.all():
        messages.warning(request, 'Access denied.')
        return redirect('scheduler-courses')

    if request.method == 'POST':

        # Supervisor actions
        if user.account_type == User.UserType.SUPERVISOR:
            # Add user
            if 'add_user' in request.POST:
                user = User.objects.filter(email=request.POST['add_user'])[0]
                course.users.add(user)

            # Remove user from course and all sections they may belong to
            if 'remove_user' in request.POST:
                user = User.objects.filter(email=request.POST['remove_user'])[0]
                course.users.remove(user)
                sections = Section.objects.filter(course=course, user=user)
                for section in sections:
                    section.user = None
                    section.save()

            # Add section
            if 'section_type' in request.POST:
                # Verify all other data is there for the new section
                try:
                    if (
                        'section_number' not in request.POST or
                        'section_start' not in request.POST or
                        'section_end' not in request.POST or
                        'section_days' not in request.POST
                    ):
                        raise ValueError
                except ValueError:
                    messages.warning(request, "Invalid section request")
                else:
                    try:
                        # Create the new section
                        section_type = request.POST['section_type']
                        section_number = request.POST['section_number']
                        section_start = datetime.strptime(request.POST['section_start'], '%H:%M').time()
                        section_end = datetime.strptime(request.POST['section_end'], '%H:%M').time()
                        section_days = request.POST['section_days']
                        Section.objects.create_section(
                            section_number,
                            course,
                            section_start,
                            meeting_end=section_end,
                            meeting_days=section_days,
                            section_type=section_type
                        )
                    except ValueError as e:
                        messages.warning(request, str(e))

            # Remove section
            if 'remove_section' in request.POST:
                Section.objects.filter(course=course, section_number=request.POST['remove_section'])[0].delete()

        # Supervisor/instructor actions
        if user.account_type == User.UserType.SUPERVISOR or user.account_type == User.UserType.INSTRUCTOR:
            # Add user to section
            if 'to_sec_num' in request.POST:
                try:
                    if 'to_sec_user' not in request.POST:
                        raise ValueError("When assigning user to a section, user must be specified.")
                    if 'remove_section' in request.POST and request.POST['remove_section'] == request.POST['to_sec_num']:
                        raise ValueError("Cannot assign user to a section that is being removed.")
                    if 'remove_user' in request.POST and request.POST['remove_user'] == request.POST['to_sec_user']:
                        raise ValueError("Cannot assign a user to a section if they are being removed from the course.")

                    section = Section.objects.filter(course=course, section_number=request.POST['to_sec_num'])[0]
                    user = User.objects.filter(email=request.POST['to_sec_user'])[0]

                    # User validation
                    if user not in course.users.all():
                        raise ValueError("A user must belong to a course to be assigned to a section of the course.")
                    if section.section_type == Section.SectionTypes.LECTURE and user.account_type != User.UserType.INSTRUCTOR:
                        raise ValueError("Only instructors can be assigned to lectures.")

                    section.user = user
                    section.save()
                except ValueError as e:
                    messages.warning(request, str(e))

            # Remove user from section
            if 'from_sec_num' in request.POST:
                try:
                    section = Section.objects.filter(course=course, section_number=request.POST['from_sec_num'])[0]
                    section.user = None
                    section.save()
                except IndexError:
                    # Will hit this if section is deleted and user is removed from section in same update
                    pass

        course.description = request.POST['course_descr']
        course.save()
        messages.success(request, course.name + " has been updated.")
        return redirect('scheduler-courses')
    else:
        all_users = User.objects.filter(~Q(account_type=User.UserType.SUPERVISOR), is_superuser=False)
        course_users = course.users.all()
        section_types = Section.SectionTypes
        meeting_days = Section.MeetingDays
        # Only display users NOT already in the course
        user_list = [user for user in all_users if user not in course_users]
        return render(
                    request, "scheduler_app/update-course.html",
                    {
                        'user': user,
                        'course': course,
                        'user_list': user_list,
                        'course_users': course_users,
                        'section_types': section_types,
                        'meeting_days': meeting_days
                    }
        )


def user_page(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    if request.method == 'GET':
        user_list = User.objects.filter(is_superuser=False)
        return render(request, "scheduler_app/users.html", {"user_list": user_list, 'user': request.user})


def add_user(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    # Get current user
    curr_user = User.objects.filter(email=request.user.email)[0]

    # Supervisor only action
    if curr_user.account_type != User.UserType.SUPERVISOR:
        messages.warning(request, "Access denied.")
        return redirect('scheduler-users')

    if request.method == 'POST':
        email = ''
        try:
            email = request.POST['email'].strip()
            password = request.POST['password'].strip()
            account_type = request.POST['type']

            user = User.objects.create_user(email=email, password=password, account_type=account_type)
            messages.success(request, user.email + " has been added.")
            return redirect('scheduler-users')
        except IntegrityError:
            messages.warning(request, email + " already exists.")
            return redirect('scheduler-users')
        except ValidationError:
            messages.warning(request, email + " is not a valid email.")
            return redirect('scheduler-users')
    else:
        return render(request, 'scheduler_app/add-user.html')


def delete_user(request, email):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    # Get current user
    curr_user = User.objects.filter(email=request.user.email)[0]

    # Supervisor only action
    if curr_user.account_type != User.UserType.SUPERVISOR:
        messages.warning(request, "Access denied.")
        return redirect('scheduler-users')

    try:
        user = User.objects.get(email=email)

        # prevent user from deleting themselves
        if user.email == curr_user.email:
            messages.warning(request, 'You cannot delete yourself.')
            return redirect('scheduler-home')

        user.delete()
        messages.success(request, email + " has been deleted.")
        return redirect('scheduler-users')
    except ObjectDoesNotExist:
        messages.warning(request, 'User not found.')
        return redirect('scheduler-users')


def user_info(request, email):
    if not request.user.is_authenticated:
        messages.error(request, 'You must login to access the site.')
        return redirect('scheduler-login')

    client = User.objects.filter(email=request.user.email)[0]

    try:
        user_data = User.objects.filter(email=email)[0]
    except IndexError:
        messages.warning(request, 'User not found.')
        return redirect('scheduler-users')

    if client.account_type != User.UserType.SUPERVISOR and client.email != user_data.email:
        messages.warning(request, 'Access denied.')
        return redirect('scheduler-home')

    # Only allow skills that the user does not already have to be added
    all_skills = Skill.objects.all()
    skill_list = []
    for skill in all_skills:
        if user_data not in skill.users.all():
            skill_list.append(skill)

    # Alphabetize list of skills
    skill_list = sorted(skill_list, key=attrgetter('name'))

    if request.method == 'POST':
        user_data.first_name = request.POST['first_name']
        user_data.last_name = request.POST['last_name']
        user_data.phone_number = request.POST['phone']
        user_data.city = request.POST['city']
        user_data.state = request.POST['state']
        user_data.address_line1 = request.POST['addr_1']
        user_data.address_line2 = request.POST['addr_2']
        user_data.zipcode = request.POST['zipcode']
        user_data.save()
        messages.success(request, "Account info updated.")

        try:
            if 'skill-add' in request.POST and 'skill-remove' in request.POST \
                    and request.POST['skill-add'] == request.POST['skill-remove']:
                raise ValueError('Cannot add a skill that is being removed.')
            else:
                if 'skill-add' in request.POST:
                    # Assign the skill to the user
                    skill = Skill.objects.filter(name=request.POST['skill-add'])[0]
                    skill.users.add(user_data)

                if 'skill-remove' in request.POST:
                    # Remove the skill from the user
                    skill = Skill.objects.filter(name=request.POST['skill-remove'])[0]
                    skill.users.remove(user_data)
        except ValueError as e:
            messages.warning(request, str(e))
        except IndexError as e:
            messages.warning(request, str(e))

        if request.user.email == user_data.email:
            return redirect('scheduler-home')
        else:
            return redirect('scheduler-users')

    return render(request, 'scheduler_app/user-info.html', {'user': user_data, 'skill_list': skill_list})


def logout_user(request):
    logout(request)
    messages.success(request, "You were logged out")
    return redirect('scheduler-login')

