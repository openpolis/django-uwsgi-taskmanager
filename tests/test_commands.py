"""Define taskmanager commands tests."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from taskmanager.models import AppCommand


class CollectTaskCommandTest(TestCase):
    """A set of tests for collect task command."""

    def test_command_output(self):
        """Test the command output."""
        out = StringIO()
        call_command("collect_commands", stdout=out)
        self.assertIn("migrate", out.getvalue())

    def test_command_output_no_djangocore(self):
        """Test the command output invoked with excludecodre argument."""
        out = StringIO()
        call_command("collect_commands", "--excludecore", stdout=out)
        self.assertNotIn("migrate", out.getvalue())

    def test_command_creation(self):
        """Test the commands creation."""
        self.assertEqual(AppCommand.objects.all().count(), 0)
        out = StringIO()
        call_command("collect_commands", stdout=out)
        self.assertNotEqual(AppCommand.objects.all().count(), 0)
