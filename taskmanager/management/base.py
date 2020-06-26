"""Base classes for writing management commands."""
import logging
import sys

from django.conf import settings
from django.core.management import BaseCommand

from taskmanager.logging import NoTerminatorStreamHandler


class LoggingBaseCommand(BaseCommand):
    """
    A subclass of BaseCommand that logs messages using the django logging system.

    The logging level is based on verbosity set with the `--verbosity` argument
    when invoking the command.

    An additional `StreamHandler` is added to the logger, pointing to
    `BaseCommand.stdout`, so that log messages are sent to that stream,
    as recommended by the documentation.

    This class also implements the `django_extension.LoggingBaseCommand.execute()`
    method, to log run time errors to the `django.commands` handler.
    This mechanism can be used to send emails when errors in management tasks happen,
    as described in the documentation for that class.

    To use a logger within the `handle()` method of your management task, create a
    management command subclassing LoggingBaseCommand, and invoke the parent's handle
    method in the `handle()` method, before the rest of the handle logic.

    .. code-block:: python

        from django_extensions.management.base import LoggingBaseCommand

        class Command(LoggingBaseCommand):
            help = 'Test logging'

            def handle(self, *args, **options):
                super(Command, self).handle(
                    __name__, *args, formatter_key="simple", **options
                )
                self.logger.info("Testing message")
    """

    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        """Handle method."""
        self.setup_logger(*args, **options)

    def setup_logger(self, name=None, formatter_key=None, **options):
        """Set up the logger."""
        if name:
            self.logger = logging.getLogger(name)
        # choose logger level based on verbosity
        verbosity = int(options.get("verbosity", 1))
        if verbosity == 0:
            self.logger.setLevel(logging.ERROR)
        elif verbosity == 1:
            self.logger.setLevel(logging.WARNING)
        elif verbosity == 2:
            self.logger.setLevel(logging.INFO)
        elif verbosity == 3:
            self.logger.setLevel(logging.DEBUG)
        # only add StreamHandler to non stdout/stderr streams
        # to avoid repetitions in log messages sent to console

        stdout_name = getattr(self.stdout, "name", None)
        if stdout_name is None or stdout_name != "<stdout>":
            # create a StreamHandler pointed to self.stdout, to be added to self.logger
            handler = NoTerminatorStreamHandler(self.stdout)
            # choose formatter for the handler,
            # using pre-defined logging Formatter,
            # if not otherwise specified in the settings
            if (
                settings.LOGGING
                and "formatters" in settings.LOGGING
                and formatter_key
                and formatter_key in settings.LOGGING["formatters"]
            ):
                handler.setFormatter(
                    logging.Formatter(
                        fmt=settings.LOGGING["formatters"][formatter_key]["format"],
                        datefmt=settings.LOGGING["formatters"][formatter_key][
                            "datefmt"
                        ],
                    )
                )
            else:
                handler.setFormatter(logging.Formatter())
            # set the level for this handler, from the logger level
            handler.setLevel(self.logger.level)
            # handler.flush = sys.stdout.flush
            self.logger.removeHandler(handler)
            self.logger.addHandler(handler)

    def execute(self, *args, **options):
        """Execute method."""
        try:
            output = super(LoggingBaseCommand, self).execute(*args, **options)
        except Exception as e:
            logger = logging.getLogger("django.commands")
            logger.error(e, exc_info=sys.exc_info(), extra={"status_code": 500})
            raise

        return output

    def create_parser(self, prog_name, subcommand, **kwargs):
        """Create a parser."""
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument(
            "--disable-notifications", action="store_true", default=False
        )
        return parser
