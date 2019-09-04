"""Define Django models for the taskmanager app."""

import datetime
import os
import re
from io import StringIO
from pathlib import Path

import slack
from django.conf import settings
from django.core.mail import send_mail
from django.core.management import call_command, load_command_class
from django.db import models
from django.utils.translation import ugettext_lazy as _
from file_read_backwards import FileReadBackwards
from uwsgidecoratorsfallback import spool

from taskmanager.settings import (
    BASE_URL,
    NOTIFICATIONS_EMAIL_FROM,
    NOTIFICATIONS_EMAIL_RECIPIENTS,
    NOTIFICATIONS_FAILURE_MESSAGE,
    NOTIFICATIONS_SLACK_CHANNELS,
    NOTIFICATIONS_SLACK_TOKEN,
    NOTIFICATIONS_WARNINGS_MESSAGE,
    TASK_MANAGER_N_LINES_IN_REPORT_LOG,
    TASK_MANAGER_N_REPORTS_INLINE,
    TASK_MANAGER_SAVE_LOGFILE,
    TASK_MANAGER_SHOW_LOGVIEWER_LINK,
)
from taskmanager.utils import log_tail

if NOTIFICATIONS_SLACK_TOKEN:
    slack_client = slack.WebClient(token=NOTIFICATIONS_SLACK_TOKEN)


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

    def emit_notification(self):

        if self.invocation_result != self.RESULT_OK:

            if NOTIFICATIONS_SLACK_TOKEN and NOTIFICATIONS_SLACK_CHANNELS:
                blocks = [
                    {
                        "type": "context",
                        "elements": [
                            {"type": "mrkdwn", "text": f"django-uwsgi-taskmanager"}
                        ],
                    }
                ]
                if self.invocation_result == self.RESULT_FAILED:
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": NOTIFICATIONS_FAILURE_MESSAGE.format(
                                    task_name=self.task.name,
                                    invocation_time=(
                                        "<!date"
                                        f"^{int(self.invocation_datetime.timestamp())}"
                                        "^{date_num} {time_secs}|???>"
                                    ),
                                ),
                            },
                        }
                    )
                else:
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": NOTIFICATIONS_WARNINGS_MESSAGE.format(
                                    task_name=self.task.name,
                                    invocation_time=(
                                        "<!date"
                                        f"^{int(self.invocation_datetime.timestamp())}"
                                        "^{date_num} {time_secs}|???>"
                                    ),
                                    n_errors=self.n_log_errors,
                                    n_warnings=self.n_log_warnings,
                                ),
                            },
                        }
                    )

                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Logs tail:\n ```{log_tail(self.log)}```",
                        },
                    }
                )

                if BASE_URL and TASK_MANAGER_SHOW_LOGVIEWER_LINK:
                    blocks.append(
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"<{BASE_URL}/taskmanager/logviewer/{self.id}|Full logs>",
                                }
                            ],
                        }
                    )

                for channel in NOTIFICATIONS_SLACK_CHANNELS:
                    slack_client.chat_postMessage(channel=channel, blocks=blocks)
                    # Fail silently

            email_settings = NOTIFICATIONS_EMAIL_FROM and NOTIFICATIONS_EMAIL_RECIPIENTS

            if email_settings:

                if self.invocation_result == self.RESULT_FAILED:
                    subject = f"{self.task.name} failed"
                    message = f"An error occurred: "
                else:
                    subject = f"{self.task.name} completed with warning"
                    message = (
                        f"{self.task.name}, "
                        f"invoked at {self.invocation_datetime}, "
                        f"completed with {self.n_log_warnings} warnings "
                        f"and {self.n_log_errors} errors."
                    )

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=NOTIFICATIONS_EMAIL_FROM,
                    recipient_list=NOTIFICATIONS_EMAIL_RECIPIENTS,
                    fail_silently=True,
                )

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
        return self.report_set.order_by("invocation_datetime").last()

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
                # NOTE: this occurs when no uWSGI is loaded (e.g. during tests)
                pass
        self.cached_next_ride = self.get_next_ride()
        self.keep_last_n_reports()
        self.save(update_fields=("spooler_id", "status", "cached_next_ride"))

    def keep_last_n_reports(self, n: int = TASK_MANAGER_N_REPORTS_INLINE):
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


@spool(pass_arguments=True)
def exec_command_task(curr_task, *args, **kwargs):
    """Execute the command of a Task."""

    curr_task.status = Task.STATUS_STARTED
    curr_task.save(update_fields=("status",))
    now = f"{datetime.datetime.now():%Y%m%d%H%M%S%f}"
    report_logfile_path = (
        f"{settings.MEDIA_ROOT}/taskmanager/logs/task_{curr_task.id}/{now}.log"
    )
    os.makedirs(os.path.dirname(report_logfile_path), exist_ok=True)
    Path(report_logfile_path).touch()
    n_log_errors = 0
    n_log_warnings = 0
    n_log_lines = 0
    n_tail_lines = TASK_MANAGER_N_LINES_IN_REPORT_LOG
    log_tail_lines = []
    report = Report.objects.create(task=curr_task, logfile=report_logfile_path)
    result = Report.RESULT_OK
    report_logfile = open(report_logfile_path, "w")
    try:
        report_logfile.write(
            (
                f"Started: {curr_task.command.name} {curr_task.arguments}"
                f" @ {datetime.datetime.now()}\n"
            )
        )
        report_logfile.flush()
        call_command(
            curr_task.command.name, *curr_task.complete_args, stdout=report_logfile
        )
        report_logfile.flush()
    except Exception as e:
        result = Report.RESULT_FAILED
        report_logfile.write(f"EXCEPTION raised: {e}")
        report_logfile.flush()
    finally:
        report_logfile.write(
            (
                f"\nFinished: {curr_task.command.name} {curr_task.arguments}"
                f" @ {datetime.datetime.now()}"
            )
        )
        report_logfile.close()
    with FileReadBackwards(report_logfile_path, encoding="utf-8") as report_logfile:
        for line in report_logfile:
            if n_log_lines < n_tail_lines:
                log_tail_lines.append(line)
            n_log_lines += 1
            if "ERROR" in line:
                n_log_errors += 1
            elif "WARNING" in line:
                n_log_warnings += 1
    hidden_lines = n_log_lines - n_tail_lines
    if hidden_lines > 0:
        log_tail_lines.append(f"{hidden_lines} lines hidden ...")
    if result == Report.RESULT_OK:
        if n_log_warnings:
            result = Report.RESULT_WARNINGS
        if n_log_errors:
            result = Report.RESULT_ERRORS
    if not TASK_MANAGER_SAVE_LOGFILE:
        try:
            os.unlink(report_logfile_path)
        except FileNotFoundError:
            pass
    report.invocation_result = result
    report.log = "\n".join(log_tail_lines[::-1])
    report.n_log_lines = n_log_lines
    report.n_log_errors = n_log_errors
    report.n_log_warnings = n_log_warnings
    report.save(
        update_fields=(
            "invocation_result",
            "log",
            "n_log_lines",
            "n_log_errors",
            "n_log_warnings",
        )
    )
    report.emit_notification()
    curr_task.cached_last_invocation_result = report.invocation_result
    curr_task.cached_last_invocation_n_errors = report.n_log_errors
    curr_task.cached_last_invocation_n_warnings = report.n_log_warnings
    curr_task.cached_last_invocation_datetime = report.invocation_datetime
    if curr_task.repetition_period:
        curr_task.status = Task.STATUS_SPOOLED
        now = datetime.datetime.now()
        if not curr_task.repetition_rate:
            curr_task.repetition_rate = 1
        if curr_task.repetition_period == Task.REPETITION_PERIOD_MINUTE:
            offset = datetime.timedelta(minutes=curr_task.repetition_rate)
        elif curr_task.repetition_period == Task.REPETITION_PERIOD_HOUR:
            offset = datetime.timedelta(hours=curr_task.repetition_rate)
        elif curr_task.repetition_period == Task.REPETITION_PERIOD_DAY:
            offset = datetime.timedelta(days=curr_task.repetition_rate)
        else:  # consider MONTH as repetition_period
            offset = datetime.timedelta(days=curr_task.repetition_rate * 365.0 / 12.0)
        next_ride = now + offset
        schedule = int(next_ride.timestamp())
        task_id = exec_command_task.spool(curr_task, at=str(schedule).encode())
        curr_task.spooler_id = task_id.decode("utf-8")
        curr_task.cached_next_ride = next_ride
    else:
        curr_task.status = Task.STATUS_IDLE
        if curr_task.spooler_id:
            # NOTE: spooler already scheduled
            spooler_path = curr_task.spooler_id.encode()
            try:
                os.unlink(spooler_path)
            except FileNotFoundError:
                # TODO: launch warning about ghost spooler lost
                pass
        curr_task.spooler_id = ""
        curr_task.cached_next_ride = None
    curr_task.keep_last_n_reports()
    curr_task.save(
        update_fields=(
            "cached_last_invocation_result",
            "cached_last_invocation_n_errors",
            "cached_last_invocation_n_warnings",
            "cached_last_invocation_datetime",
            "status",
            "repetition_rate",
            "spooler_id",
            "cached_next_ride",
        )
    )
