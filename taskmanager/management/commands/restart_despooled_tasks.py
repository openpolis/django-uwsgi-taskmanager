import datetime
from taskmanager.management.base import LoggingBaseCommand
from os.path import exists
from taskmanager.models import Task


class Command(LoggingBaseCommand):
    """Command to re-start all tasks being in a SPOOLED state, but missing the spooler file.

    This happens when a container restarts and no volume is there for the peristence.
    """

    help = "Command to re-start all de-spooled tasks (being in a SPOOLED state, but missing the spooler file)."

    verbosity = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            dest="dry_run", action='store_true',
            help="Show logs, do not modify data in DB.",
        )

    def handle(self, *args, **options):
        self.setup_logger(__name__, formatter_key="simple", **options)

        dry_run = options['dry_run']

        spooled_tasks = Task.objects.filter(status='spooled')
        if spooled_tasks:
            self.logger.info(
                f"{spooled_tasks.count()} de-spooled tasks found that need to be re-started were found."
            )
            if dry_run:
                self.logger.info("Dry run mode (changes will not be persisted).")
            else:
                self.logger.info("Proceeding.")

            for t in spooled_tasks:
                if not exists(t.spooler_id):
                    # reset task's scheduling to tomorrw, same hour and minute
                    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                    t.scheduling = datetime.datetime(
                        year=tomorrow.year,
                        month=tomorrow.month,
                        day=tomorrow.day,
                        hour=t.scheduling.hour,
                        minute=t.scheduling.minute
                    )

                    if dry_run:
                        self.logger.info(f"Task {t} would be restarted. Next launch would be at {t.get_next_ride()}")
                    else:
                        self.logger.info(f"Task {t} restarted. Next launch will be at {t.get_next_ride()}")
                        t.save()
                        t.stop()
                        t.start()

            self.logger.info("Procedure completed.")
        else:
            self.logger.info("No de-spooled tasks found.")
