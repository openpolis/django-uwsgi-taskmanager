"""Define taskmanager utils tests."""

from django.test import TestCase

from taskmanager.models import AppCommand, Report, Task
from taskmanager.utils import log_tail


class TestUtils(TestCase):
    """A set of tests for utils."""

    def setUp(self):
        """Prepare initial data for testing."""
        self.command_check, _ = AppCommand.objects.get_or_create(
            name="check", app_name="django.core", defaults={"active": True}
        )
        self.task3, _ = Task.objects.get_or_create(
            name="task test 3", command=self.command_check, arguments=""
        )
        self.report3, _ = Report.objects.get_or_create(
            task=self.task3,
            invocation_result="failed",
            log=(
                "Started: test_command at 2019-01-07 16:49:03.929006\n"
                "EXCEPTION raised: min() arg is an empty sequence\n"
                "Finished: test_command at 2019-01-07 16:49:03.934684\n"
            ),
        )

    def test_log_tail(self):
        """Test the log tail function."""
        self.assertEqual(
            log_tail(self.report3.log),
            (
                "Started: test_command at 2019-01-07 16:49:03.929006\n"
                "EXCEPTION raised: min() arg is an empty sequence\n"
                "Finished: test_command at 2019-01-07 16:49:03.934684\n"
            ),
        )
        self.assertEqual(
            log_tail(self.report3.log, 2),
            (
                "2 lines hidden ...\n"
                "Finished: test_command at 2019-01-07 16:49:03.934684\n"
            ),
        )
