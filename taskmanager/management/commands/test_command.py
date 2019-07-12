"""Test command."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command for test purpouse."""

    help = "Command for test purpouse"

    def add_arguments(self, parser):
        """Add arguments method."""
        parser.add_argument("arg1", default=None, help="Test arg1")
        parser.add_argument("arg2", default=None, help="Test arg2")
        parser.add_argument("-a", action="store_true", dest="action_a", help="Test -a")
        parser.add_argument("-b", action="store_true", dest="action_b", help="Test -b")
        parser.add_argument(
            "--arg3",
            action="append",
            dest="arg3",
            nargs="?",
            type=str,
            default="",
            help="Test arg3",
        )

    def handle(self, *args, **options):
        """Handle method."""
        self.stdout.write(str(options["arg1"]))
        self.stdout.write(str(options["arg2"]))
        self.stdout.write(str(options["action_a"]))
        self.stdout.write(str(options["action_b"]))
        self.stdout.write(str(options["arg3"]))
