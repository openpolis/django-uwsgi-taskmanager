"""Define uWSGI exec command tasks for the taskmanager app."""

import datetime
import os
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from file_read_backwards import FileReadBackwards
from uwsgidecoratorsfallback import spool


@spool(pass_arguments=True)
def exec_command_task(curr_task, *args, **kwargs):
    """Execute the command of a Task."""
    from taskmanager.models import Report, Task

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
    n_tail_lines = getattr(settings, "TASK_MANAGER_N_LINES_IN_REPORT_LOG", 10)
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
    if not getattr(settings, "TASK_MANAGER_SAVE_LOGFILE", True):
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
