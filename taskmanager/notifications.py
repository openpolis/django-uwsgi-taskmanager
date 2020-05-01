from abc import ABC
from typing import Dict, Union

from django.urls import reverse

from taskmanager.models import Report
from taskmanager.utils import get_base_url, log_tail

try:
    import slack

except ImportError:  # pragma: no cover
    slack = None


class Notifications:
    """
    A registry for notification handlers
    """


LEVEL_OK = 0
LEVEL_WARNINGS = 10
LEVEL_ERRORS = 20
LEVEL_FAILED = 30

LEVEL_DEFAULT = LEVEL_OK

invocation_result_to_level_map = {
    "ok": LEVEL_OK,
    "warnings": LEVEL_WARNINGS,
    "errors": LEVEL_ERRORS,
    "failed": LEVEL_FAILED,
}


class NotificationHandler(ABC):
    messages: Dict[int, str] = {
        LEVEL_OK: (
            'Task *"{task_name}"* invoked at {invocation_time} '
            "completed successfully. "
        ),
        LEVEL_WARNINGS: (
            'Task *"{task_name}"* invoked at {invocation_time} '
            "completed successfully "
            "with *{n_errors}* errors and *{n_warnings}* warnings."
        ),
        LEVEL_ERRORS: (
            'Task *"{task_name}"* invoked at {invocation_time} '
            "completed successfully "
            "with *{n_errors}* errors and *{n_warnings}* warnings."
        ),
        LEVEL_FAILED: ('Task *"{task_name}"* invoked at {invocation_time} *failed*.'),
    }
    level: int

    def __init__(self, level: Union[int, str] = LEVEL_DEFAULT):
        if isinstance(level, int):
            self.level = level
        elif isinstance(level, str):
            self.level = invocation_result_to_level_map.get(level, LEVEL_OK)

    def emit(self, report: Report):
        raise NotImplementedError


class SlackNotificationHandler(NotificationHandler):
    def __new__(cls, *args, **kwargs):

        if slack:  # Only create a new instance if "slack" module is available
            return super().__new__(cls)

    def __init__(
        self, token: str, channel: str, level: Union[int, str] = LEVEL_DEFAULT,
    ):

        self.client = slack.WebClient(token=token)

        self.channel = channel

        super().__init__(level)

    def emit(self, report: Report):
        result = invocation_result_to_level_map.get(report.invocation_result)

        text = self.messages.get(result)
        text = text.format(
            task_name=report.task.name,
            invocation_time=int(report.invocation_datetime.timestamp()),
            n_warnings=report.n_log_warnings,
            n_errors=report.n_log_errors,
        )

        base_url = get_base_url()
        logviewer_url = reverse("log_viewer", args=(report.id,))

        blocks = [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "django-uwsgi-taskmanager",
                    }
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"<http://{base_url}{logviewer_url}|Full logs>",
                    }
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "Logs tail:\n"
                        f"```{log_tail(report.log)}```"
                    ),
                },
            },
        ]

        # Finally, post message to channel (fail silently)
        self.client.chat_postMessage(channel=self.channel, blocks=blocks)


#
# class EmailNotificationHandler(NotificationHandler):
#     def __init__(self):
#         pass
#
#     def emit(self):
#         if self.invocation_result == self.RESULT_FAILED:
#             subject = f"{self.task.name} failed"
#             message = f"An error occurred: "
#         else:
#             subject = f"{self.task.name} completed with warning"
#             message = (
#                 f"{self.task.name}, "
#                 f"invoked at {self.invocation_datetime}, "
#                 f"completed with {self.n_log_warnings} warnings "
#                 f"and {self.n_log_errors} errors."
#             )
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_FROM,
#             recipient_list=UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_RECIPIENTS,
#             fail_silently=True,
#         )
