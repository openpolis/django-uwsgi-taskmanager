"""Collect task command."""

import logging
from io import StringIO

import django.test
from django.core.management import call_command


class TaskManagerTest(django.test.TestCase):
    """A set of tests for collect task command."""

    def setUp(self):
        """Logger handlers need to be reset before each tests or they mangle up."""
        logger = logging.getLogger(
            "project.tasks.management.commands.test_logging_command"
        )
        logger.handlers = []

    def test_command(self):
        """Test the command output."""
        out = StringIO()
        call_command(
            "test_logging_command", verbosity=3, debug="test_debug", stdout=out
        )
        out.seek(0)
        lines = out.readlines()
        found = False
        for line in lines:
            found = found or (line == "\n")
        self.assertFalse(found)
