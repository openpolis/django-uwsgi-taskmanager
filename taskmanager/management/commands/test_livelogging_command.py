"""Test live logging command."""
import time
from taskmanager.management.base import LoggingBaseCommand


class Command(LoggingBaseCommand):
    """Command for testing live logger. Perform a simple iteration, up to a maximum limit,
    sleeping 0.1 seconds between each number generation.

    Generates 10 numbers per second, logging them at debug level.
    Every 100 iterations generates an info message, shoinw global process.

    """

    help = "Command for testing live logger"
    verbosity = None

    def add_arguments(self, parser):
        """Add arguments method."""
        parser.add_argument(
            "--limit", default="1000", dest="limit", type=int, help="Limit the max iteration number"
        )

    def handle(self, *args, **options):
        """Handle method."""
        self.setup_logger(__name__, formatter_key="simple", **options)

        for n in range(1, options['limit'] + 1):
            self.logger.debug(f"{n}")
            time.sleep(0.1)
            if n % 100 == 0:
                self.logger.info(f"{n}/{options['limit']}")
