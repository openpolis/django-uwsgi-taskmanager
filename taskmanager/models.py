"""Define Django models for the taskmanager app."""

import datetime
import os
import re
from io import StringIO

from django.conf import settings
from django.core.management import load_command_class
from django.db import models
from django.utils.translation import ugettext_lazy as _

from taskmanager.tasks import exec_command_task


# FIXME: remove after migration squash
def task_directory_path(instance, filename):
    """
    Return the file path within a task_id in the MEDIA_ROOT.

    e.g. file will be uploaded to MEDIA_ROOT/taskmanager/logs/task_<id>/<filename>
    """
    return f"taskmanager/logs/task_{instance.task_id}/{filename}"


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

    # FIXME: iterate over the file instead of read all lines in memory
    def get_log_lines(self):
        """Return log lines from logfile or log field."""
        try:
            log_lines = "".join(open(self.logfile, "r").readlines()).split("\n")
        except FileNotFoundError:
            log_lines = self.log.split("\n")
        return log_lines

    class Meta:
        """Django model options."""

        verbose_name = _("Report")
        verbose_name_plural = _("Reports")


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
    """A command related task."""

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
        blank=True, null=True, verbose_name=_("Next")
    )

    @property
    def last_report(self):
        """Get the last report of the task."""
        try:
            # NOTE: last() don't work with prefetch_related
            return self.report_set.all()[0]
        except IndexError:
            return None

    @property
    def last_invocation_result(self):
        """Get the last invocation result."""
        return self.last_report.invocation_result if self.last_report else None

    @property
    def last_invocation_datetime(self):
        """Get the last invocation date and time."""
        return self.last_report.invocation_datetime if self.last_report else None

    def get_next_ride(self):
        """Get the next ride."""
        if self.repetition_period and self.status == self.STATUS_SPOOLED:
            if self.repetition_rate in (None, 0):
                # FIXME: move this logic in class
                # consider 1 as default repetition_rate
                self.repetition_rate = 1
            if self.repetition_period == self.REPETITION_PERIOD_MINUTE:
                offset = datetime.timedelta(minutes=self.repetition_rate)
            elif self.repetition_period == self.REPETITION_PERIOD_HOUR:
                offset = datetime.timedelta(hours=self.repetition_rate)
            elif self.repetition_period == self.REPETITION_PERIOD_DAY:
                offset = datetime.timedelta(days=self.repetition_rate)
            else:
                # FIXME: move this logic in class
                # consider MONTH as default repetition_period
                offset = datetime.timedelta(days=self.repetition_rate * 365.0 / 12.0)
            next_ride = self.last_invocation_datetime + offset
        elif self.scheduling and self.status == Task.STATUS_SCHEDULED:
            next_ride = self.scheduling
        else:
            next_ride = None
        return next_ride

    @property
    def _args_dict(self):
        res = {}
        if not self.arguments or self.arguments.strip() == "":
            return res
        args = re.split(r"\s*,{1}\s*", self.arguments)
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
        try:
            task_id = exec_command_task.spool(self, **kwargs)
        except Exception as e:
            Report.objects.create(
                task=self,
                invocation_result=Report.RESULT_FAILED,
                log=f"TASK SPOOL FAILED!!!\n{e}",
            )
        else:
            try:
                self.spooler_id = task_id.decode("utf-8")
            except AttributeError:
                # NOTE: this occurs when no UWSGI is loaded (e.g. during tests)
                pass
        self.cached_next_ride = self.get_next_ride()
        self.keep_last_n_reports()
        self.save(update_fields=("spooler_id", "status", "cached_next_ride"))

    def keep_last_n_reports(self):
        """Delete all task's reports but a number defined in settings."""
        if getattr(settings, "TASK_MANAGER_N_REPORTS_INLINE", 0) > 0:
            last_n_reports_ids = (
                Report.objects.filter(task=self)
                .order_by("-id")[: settings.TASK_MANAGER_N_REPORTS_INLINE]
                .values_list("id", flat=True)
            )
            Report.objects.filter(task=self).exclude(
                pk__in=list(last_n_reports_ids)
            ).delete()

    class Meta:
        """Django model options."""

        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
