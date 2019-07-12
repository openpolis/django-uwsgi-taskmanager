"""Define taskmanager models tests."""

from django.test import TestCase, tag

from taskmanager.models import AppCommand, Report, Task


class TestAppCommandModel(TestCase):
    """A set of tests for application command."""

    def setUp(self):
        """Prepare initial data for testing."""
        self.command_check, _ = AppCommand.objects.get_or_create(
            name="test_command", app_name="taskmanager", defaults={"active": True}
        )

    def test_str(self):
        """Test the str method to represent a command."""
        self.assertEqual(str(self.command_check), "taskmanager: test_command")


class TestTaskModel(TestCase):
    """A set of tests for tasks."""

    def setUp(self):
        """Prepare initial data for testing."""
        self.command_check, _ = AppCommand.objects.get_or_create(
            name="test_command", app_name="taskmanager", defaults={"active": True}
        )
        self.task1, _ = Task.objects.get_or_create(
            name="task test 1",
            command=self.command_check,
            arguments="arg1, arg2,-a, -b, --arg3 param1",
        )
        self.task2, _ = Task.objects.get_or_create(
            name="task test 2", command=self.command_check, arguments=""
        )
        self.report1, _ = Report.objects.get_or_create(
            task=self.task1, invocation_result="ok", log=""
        )
        self.report2, _ = Report.objects.get_or_create(
            task=self.task1, invocation_result="ok", log=""
        )

    def test_last_report(self):
        """Test the last report."""
        self.assertEqual(self.task1.last_report, self.report2)
        self.assertEqual(self.task2.last_report, None)

    def test_last_invocation_result(self):
        """Test the last invocation result."""
        self.assertEqual(
            self.task1.last_invocation_result, self.report2.invocation_result
        )
        self.assertEqual(self.task2.last_invocation_result, None)

    def test_last_invocation_datetime(self):
        """Test the last invocation datetime."""
        self.assertEqual(
            self.task1.last_invocation_datetime, self.report2.invocation_datetime
        )
        self.assertEqual(self.task2.last_invocation_datetime, None)

    def test_args_dict(self):
        """Test the args dict."""
        self.assertDictEqual(
            self.task1._args_dict,
            {"arg1": None, "arg2": None, "-a": None, "-b": None, "--arg3": "param1"},
        )
        self.assertDictEqual(self.task2._args_dict, {})

    def test_args(self):
        """Test the args."""
        self.assertSequenceEqual(self.task1.args, ["arg1", "arg2", "-a", "-b"])

    def test_args_options(self):
        """Test the args option."""
        self.assertDictEqual(self.task1.options, {"arg3": "param1"})

    def test_str(self):
        """Test the str method to represent a task."""
        self.assertEqual(str(self.task1), "task test 1 (idle)")

    @tag("async")
    def test_launch(self):
        """Test task launch."""
        self.task1.launch()
        task1_new_report_generated = Report.objects.last()
        self.assertEqual(self.task1.last_report, task1_new_report_generated)
        self.task2.launch()
        task2_new_report_generated = Report.objects.last()
        self.assertEqual(self.task2.last_report, task2_new_report_generated)


class TestReportModel(TestCase):
    """A set of tests for reports."""

    def setUp(self):
        """Prepare initial data for testing."""
        self.command_check, _ = AppCommand.objects.get_or_create(
            name="check", app_name="django.core", defaults={"active": True}
        )
        self.task1, _ = Task.objects.get_or_create(
            name="task test 1", command=self.command_check, arguments=""
        )
        self.report1, _ = Report.objects.get_or_create(
            task=self.task1, invocation_result="ok", log=""
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

    def test_str(self):
        """Test the str method to represent a task."""
        self.assertEqual(
            str(self.report1),
            f"Report task test 1 ok {self.report1.invocation_datetime}",
        )

    def test_get_log_lines(self):
        """Test the get_log_lines function."""
        self.assertListEqual(
            self.report3.get_log_lines(),
            [
                "Started: test_command at 2019-01-07 16:49:03.929006",
                "EXCEPTION raised: min() arg is an empty sequence",
                "Finished: test_command at 2019-01-07 16:49:03.934684",
                "",
            ],
        )
