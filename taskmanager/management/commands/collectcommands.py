"""Collect task command."""

from django.core.management import get_commands
from django.core.management.base import BaseCommand

from taskmanager.models import AppCommand


class Command(BaseCommand):
    """Collect all the available commands and sync them with the database."""

    help = "Collect all the available commands and sync them with the database"

    def add_arguments(self, parser):
        """Add arguments method."""
        parser.add_argument(
            "--excludecore",
            action="store_true",
            dest="excludecore",
            help="Exclude django.core commands from the list",
        )

    def handle(self, *args, **options):
        """Handle method."""
        exclude_core = options.get("excludecore", False)
        for command, app in get_commands().items():
            if not (exclude_core and app.startswith("django")):
                AppCommand.objects.get_or_create(name=command, app_name=app)
                self.stdout.write(f"{app}: {command}")
