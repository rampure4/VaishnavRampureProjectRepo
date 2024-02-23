# Getting started in the scheduler app
Below is a guide for creating users in the system. Django's default concept of a User has been overridden with a custom 
User class that inherits from Django's `AbstractUser` class. Users will log in via their email and password instead of a 
username and password. Users also contain additional data members for contact information and account type. A User can 
either be a TA, Instructor, or Supervisor and will have different privileges in the system based on this role. When 
logging in, emails are case-insensitive.

# Creating a superuser
The process of creating a superuser has not changed much at all. The only difference will be the need to supply an email 
and password, as opposed to the default username and password.

# Creating a user in the system
To properly create a user in the system, please follow these steps:
1. Delete the existing `db.sqlite3` file you may have
2. Run the `manage.py` console via either of these options
   1. Tools -> Run manage.py Task...
   2. CTRL + ALT + R
3. Run the `migrate scheduler_app` command
4. Run the `migrate` command (without specifying an appname)
5. Launch the Python console from either your preferred CLI or via PyCharm's window
6. Run the following commands from the Python console
   1. `from scheduler_app.models import User`
   2. `User.objects.create_user("jdoe@uwm.edu", "myPassword123", User.UserType.Supervisor)` (with any additional kwargs following)
7. A line should be printed that displays the new User's email `<User: jdoe@uwm.edu>`
8. The new User can now be viewed from the admin panel along with any superusers that were created.

Please note that adding a new User from the admin panel is incorrect. The password for the User will not be hashed when
created this way. The login process expects this hashing to have been done when the password from the request is 
compared to the database. As a result, the user will not be able to log in despite having an account.

# Populating Skills List
Currently, the list of skills is predetermined for users to select from. To add skills to the database, please add them via the python console:
1. `from scheduler_app.models import Skill`
2. `Skill.objects.create_skill("Java")`
3. `Skill.objects.create_skill("English")`
4. ...
