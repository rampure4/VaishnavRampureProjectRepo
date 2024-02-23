from django.test import TestCase
from scheduler_app.models import Skill
from django.db.utils import IntegrityError
from django.db import transaction


# These Unit Tests evaluate the Skill model.
class SkillModelTest(TestCase):
    # Ensure a new Skill can be created and its data is correct.
    def test_create_skill(self):
        Skill.objects.create_skill('Programming')

        skill_list = Skill.objects.all()
        self.assertEqual(1, skill_list.__len__(), msg='Incorrect number of Skills created.')

        skill = skill_list[0]
        self.assertEqual('Programming', skill.name, msg='New Skill has incorrect name.')

    # Ensure the overridden __str__ method presents the Skill's name.
    def test_skill_to_string(self):
        Skill.objects.create_skill('Programming')

        skill_list = Skill.objects.all()
        skill = skill_list[0]
        self.assertEqual('Programming', skill.__str__(), msg='New Skill has incorrect string representation.')

    # Ensure it is forbidden to create a second Skill with the same name as the first.
    def test_create_duplicate_skill(self):
        Skill.objects.create_skill('Programming')

        with self.assertRaises(IntegrityError, msg='Duplicate Skill did not throw IntegrityError.'):
            with transaction.atomic():
                Skill.objects.create_skill('Programming')

        skill_list = Skill.objects.all()
        self.assertEqual(1, skill_list.__len__(), msg='Incorrect number of Skills created.')

    # Ensure a Skill cannot be created with no arguments.
    def test_section_no_ags(self):
        with self.assertRaises(TypeError, msg='Creating a Skill with no arguments did not throw TypeError.'):
            Skill.objects.create_skill()

    # Ensure it is allowed to create three Skills with different names.
    def test_create_skill_series(self):
        Skill.objects.create_skill('Singing')
        Skill.objects.create_skill('Dancing')
        Skill.objects.create_skill('Playing Guitar')

        skill_list = Skill.objects.all()
        self.assertEqual(3, skill_list.__len__(), msg='Incorrect number of Skills created.')

        skill1 = skill_list[0]
        self.assertEqual('Singing', skill1.name, msg='New Skill 1 has incorrect name.')

        skill2 = skill_list[1]
        self.assertEqual('Dancing', skill2.name, msg='New Skill 2 has incorrect name.')

        skill3 = skill_list[2]
        self.assertEqual('Playing Guitar', skill3.name, msg='New Skill 3 has incorrect name.')
