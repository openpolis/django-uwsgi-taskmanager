"""Test live logging command."""
import random
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
        parser.add_argument(
            "--trace-steps", default="10", dest="trace_steps", type=int, help="Number of steps to emit a trace info"
        )
        parser.add_argument(
            "--error-prob", default="5", dest="error_prob", type=int, help="Probability of error emission (%)"
        )
        parser.add_argument(
            "--warning-prob", default="15", dest="warning_prob", type=int, help="Probability of warning emission (%)"
        )

    def handle(self, *args, **options):
        """Handle method."""
        self.setup_logger(__name__, formatter_key="simple", **options)

        random.seed()
        for n in range(1, options['limit'] + 1):
            self.logger.debug(f"A debug message was generated ({n})")
            err_dice = random.randint(0, 100)
            warn_dice = random.randint(0, 100)

            if err_dice < options['error_prob']:
                self.logger.error("An error was generated rendomly")
            if warn_dice < options['warning_prob']:
                self.logger.warning("A warning was generated randomly")
            time.sleep(0.1)
            if n % options['trace_steps'] == 0:
                self.logger.info(f"{n}/{options['limit']}")
