"""Define Django models for the taskmanager app."""
import calendar
import datetime
import os
import re
from io import StringIO
from typing import Dict

import pytz
from django.core.management import load_command_class
from django.db import models
from django.utils.translation import ugettext_lazy as _

from taskmanager import notifications
from taskmanager.settings import UWSGI_TASKMANAGER_N_REPORTS_INLINE
from taskmanager.tasks import exec_command_task


class AppCommand(models.Model):
    """An application command representation."""

    name = models.CharField(max_length=100)
    app_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def get_command_class(self):
        """Get the command class."""
        return load_command_class(app_name=self.app_name, name=self.name)

    @property
    def help_text(self):
        """Get the command help text."""
        output = StringIO()
        command_class = self.get_command_class()
        command_class.create_parser("", self.name).print_help(file=output)
        return output.getvalue()

    def __str__(self):
        """Return the string representation of the app command."""
        return f"{self.app_name}: {self.name}"

    class Meta:
        """Django model options."""

        verbose_name = _("Command")
        verbose_name_plural = _("Commands")


class Report(models.Model):
    """A report of a task execution with log."""

    RESULT_NO = ""
    RESULT_OK = "ok"
    RESULT_FAILED = "failed"
    RESULT_ERRORS = "errors"
    RESULT_WARNINGS = "warnings"
    RESULT_CHOICES = (
        (RESULT_NO, "---"),
        (RESULT_OK, "OK"),
        (RESULT_FAILED, "FAILED"),
        (RESULT_ERRORS, "ERRORS"),
        (RESULT_WARNINGS, "WARNINGS"),
    )

    task = models.ForeignKey("Task", on_delete=models.CASCADE)
    invocation_result = models.CharField(
        max_length=20, choices=RESULT_CHOICES, default=RESULT_NO
    )
    invocation_datetime = models.DateTimeField(auto_now_add=True)
    log = models.TextField(blank=True)
    logfile = models.FilePathField(
        path="/", match="*.log", recursive=True, max_length=4096, blank=True, default=""
    )
    n_log_lines = models.PositiveIntegerField(null=True, blank=True)
    n_log_errors = models.PositiveIntegerField(null=True, blank=True)
    n_log_warnings = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        """Return the string representation of the app command."""
        return (
            f"Report {self.task.name} {self.invocation_result}"
            f" {self.invocation_datetime}"
        )

    def get_log_lines(self):
        # FIXME: iterate over the file instead of read all lines in memory
        """Return log lines from logfile or log field."""
        try:
            log_lines = "".join(open(self.logfile, "r").readlines()).split("\n")
        except FileNotFoundError:
            log_lines = self.log.split("\n")
        return log_lines

    def read_log_lines(self, offset: int):
        """Uses an offset to read just lines of the log file not yet read.

        :param: offset parameter in bytes

        :return: 2-tuple (list, int)
          - list of lines of log files from offset
          - the size of the file in bytes
        """
        if os.path.exists(self.logfile):
            fh = open(self.logfile, "r")
            fh.seek(offset)
            log_lines = [line.strip('\n') for line in fh]
            log_size = fh.tell()
            fh.close()
            return log_lines, log_size
        else:
            return [], None

    def emit_notifications(self):
        """Emit a slack or email notification."""
        if not self.invocation_result:
            return

        handlers: Dict[str, notifications.NotificationHandler]
        handlers = self._meta.app_config.notification_handlers

        for handler in handlers.values():
            handler.handle(self)


class TaskCategory(models.Model):
    """A task category, used to group tasks when numbers go up."""

    name = models.CharField(max_length=255)

    def __str__(self):
        """Return the string representation of the task category."""
        return self.name

    class Meta:
        """Django model options."""

        verbose_name = _("Task category")
        verbose_name_plural = _("Tasks categories")


class Task(models.Model):
    """
    A command related task.

    Represents a management command with a defined set of arguments (

    """

    REPETITION_PERIOD_MINUTE = "minute"
    REPETITION_PERIOD_HOUR = "hour"
    REPETITION_PERIOD_DAY = "day"
    REPETITION_PERIOD_MONTH = "month"
    REPETITION_PERIOD_CHOICES = (
        (REPETITION_PERIOD_MINUTE, "MINUTE"),
        (REPETITION_PERIOD_HOUR, "HOUR"),
        (REPETITION_PERIOD_DAY, "DAY"),
        (REPETITION_PERIOD_MONTH, "MONTH"),
    )

    STATUS_IDLE = "idle"
    STATUS_SPOOLED = "spooled"
    STATUS_SCHEDULED = "scheduled"
    STATUS_STARTED = "started"
    STATUS_CHOICES = (
        (STATUS_IDLE, "IDLE"),
        (STATUS_SPOOLED, "SPOOLED"),
        (STATUS_SCHEDULED, "SCHEDULED"),
        (STATUS_STARTED, "STARTED"),
    )

    name = models.CharField(max_length=255)
    command = models.ForeignKey(
        AppCommand, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )
    arguments = models.TextField(
        blank=True,
        help_text=_(
            'Separate arguments with a comma ","'
            'and parameters with a blank space " ". '
            "eg: -f, --secondarg param1 param2, --thirdarg=pippo, --thirdarg"
        ),
    )
    category = models.ForeignKey(
        "TaskCategory",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        help_text=_("Choose a category for this task"),
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_IDLE, editable=False
    )
    scheduling = models.DateTimeField(blank=True, null=True)
    repetition_period = models.CharField(
        max_length=20, choices=REPETITION_PERIOD_CHOICES, blank=True
    )
    repetition_rate = models.PositiveSmallIntegerField(blank=True, null=True)
    spooler_id = models.FilePathField(
        path="/",
        match="uwsgi_spoolfile_on_*",
        recursive=True,
        max_length=255,
        blank=True,
    )
    note = models.TextField(
        blank=True, null=True, help_text=_("A note on how this task is used.")
    )

    cached_last_invocation_datetime = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Last datetime")
    )
    cached_last_invocation_result = models.CharField(
        max_length=20,
        choices=Report.RESULT_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Last result"),
    )
    cached_last_invocation_n_errors = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Errors")
    )
    cached_last_invocation_n_warnings = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Warnings")
    )
    cached_next_ride = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Next"),
    )

    @property
    def last_report(self):
        """Get the last report of the task."""
        return self.report_set.order_by("invocation_datetime").last()

    @property
    def last_invocation_result(self):
        """Get the last invocation result."""
        return self.last_report.invocation_result if self.last_report else None

    @property
    def last_invocation_datetime(self):
        """Get the last invocation date and time."""
        return self.last_report.invocation_datetime if self.last_report else None

    def get_next_ride(self) -> datetime.datetime:
        """Get the next ride."""
        utc_tz = pytz.timezone('UTC')
        if self.repetition_period and self.status in [self.STATUS_SPOOLED, self.STATUS_STARTED]:
            now = self.last_invocation_datetime or datetime.datetime.now().replace(tzinfo=utc_tz)

            if self.repetition_rate in (None, 0):
                # consider 1 as default repetition_rate
                self.repetition_rate = 1
            if self.repetition_period == self.REPETITION_PERIOD_MINUTE:
                offset = datetime.timedelta(minutes=self.repetition_rate)
                _next = (
                    datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, 0, tzinfo=utc_tz)
                    + offset
                    + datetime.timedelta(seconds=self.scheduling.second)
                )
            elif self.repetition_period == self.REPETITION_PERIOD_HOUR:
                offset = datetime.timedelta(hours=self.repetition_rate)
                _next = (
                    datetime.datetime(now.year, now.month, now.day, now.hour, 0, 0, tzinfo=utc_tz)
                    + offset
                    + datetime.timedelta(
                        minutes=self.scheduling.minute,
                        seconds=self.scheduling.second
                    )
                )
            elif self.repetition_period == self.REPETITION_PERIOD_DAY:
                offset = datetime.timedelta(days=self.repetition_rate)
                _next = (
                    datetime.datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=utc_tz)
                    + offset
                    + datetime.timedelta(
                        hours=self.scheduling.hour,
                        minutes=self.scheduling.minute,
                        seconds=self.scheduling.second
                    )
                )
            else:
                # monthly scheduling requires a different computation
                def add_months(sourcedate, months):
                    month = sourcedate.month - 1 + months
                    year = sourcedate.year + month // 12
                    month = month % 12 + 1
                    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
                    return datetime.datetime(year, month, day, tzinfo=utc_tz)

                _next = (
                    add_months(now, self.repetition_rate)
                    + datetime.timedelta(
                        hours=self.scheduling.hour,
                        minutes=self.scheduling.minute,
                    )
                )

            # scheduled task should start at scheduled time
            # if the scheduled time has already passed, then execution is set in 10 seconds
            if _next <= now:
                next_ride = now + datetime.timedelta(seconds=10)
            else:
                next_ride = _next
        elif self.scheduling and self.status == Task.STATUS_SCHEDULED:
            next_ride = self.scheduling
        else:
            next_ride = None

        if next_ride:
            next_ride = next_ride.replace(tzinfo=utc_tz)
        return next_ride

    @property
    def _args_dict(self):
        res = {}
        if not self.arguments or self.arguments.strip() == "":
            return res
        args = re.split(r"\s*,\s*", self.arguments)
        for arg in args:
            arg_chunks = re.split(r"[\s=]?\s+", arg, 1)
            argument = arg_chunks[0].strip(" =")
            try:
                params = arg_chunks[1].strip(" =")
            except IndexError:
                params = None
            res[argument] = params
        return res

    @property
    def args(self):
        """Get the task args."""
        return [f"{x}" for x, y in self._args_dict.items() if not y]

    @property
    def options(self):
        """Get the task options."""
        return {
            f"{x}".strip("-").replace("-", "_"): f"{y}"
            for x, y in self._args_dict.items()
            if y
        }

    @property
    def complete_args(self):
        """Get all task args in order to avoid problems with required options.

        As suggested here:
        https://stackoverflow.com/questions/32036562/call-command-argument-is-required
        """
        return list(
            filter(
                lambda x: x is not None,
                (
                    item
                    for sublist in [(k, v) for k, v in self._args_dict.items()]
                    for item in sublist
                ),
            )
        )

    def __str__(self):
        """Return the string representation of the task."""
        return f"{self.name} ({self.status})"

    def delete(self, *args, **kwargs):
        """Stop and delete the task itself."""
        self.stop()
        super().delete(*args, **kwargs)

    def stop(self):
        """Stop the task itself removing the scheduled spooler."""
        if self.spooler_id:
            spooler_path = self.spooler_id.encode()
            try:
                os.unlink(spooler_path)
            except FileNotFoundError:
                # TODO: launch warning about ghost spooler lost
                pass
        self.spooler_id = ""
        self.status = self.STATUS_IDLE
        self.keep_last_n_reports()
        self.cached_next_ride = self.get_next_ride()
        self.save(update_fields=("spooler_id", "status", "cached_next_ride"))

    def launch(self):
        """Launch the task itself."""
        if self.spooler_id:
            # NOTE: spooler already scheduled
            spooler_path = self.spooler_id.encode()
            try:
                os.unlink(spooler_path)
            except FileNotFoundError:
                # TODO: launch warning about ghost spooler lost
                pass
        self.status = self.STATUS_SPOOLED
        self.save(update_fields=("status",))
        kwargs = {}
        if self.scheduling:
            self.status = Task.STATUS_SCHEDULED
            schedule = int(self.scheduling.timestamp())
            # NOTE: spool at param requires bytes
            kwargs["at"] = str(schedule).encode()

        # Spool the execution of the command
        task_id = exec_command_task.spool(self, **kwargs)
        if task_id:
            self.spooler_id = task_id.decode("utf-8")
        else:
            # This probably means the uWSGI spooler is unavailable and
            # the task executed synchronously (e.g. during tests).
            pass

        self.cached_next_ride = self.get_next_ride()
        self.save(update_fields=("spooler_id", "status", "cached_next_ride"))

    def keep_last_n_reports(self, n: int = UWSGI_TASKMANAGER_N_REPORTS_INLINE):
        """Delete all Task's Reports except latest `n` Reports."""
        if n:
            last_n_reports_ids = (
                Report.objects.filter(task=self)
                .order_by("-id")[:n]
                .values_list("id", flat=True)
            )
            Report.objects.filter(task=self).exclude(
                pk__in=list(last_n_reports_ids)
            ).delete()

    class Meta:
        """Django model options."""

        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
