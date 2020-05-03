from abc import ABC
from typing import TYPE_CHECKING, Dict, List, Union

from django.core.mail import send_mail
from django.urls import reverse

from taskmanager.utils import get_base_url, log_tail

if TYPE_CHECKING:
    from taskmanager.models import Report


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

    def emit(self, report: "Report"):
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

    def emit(self, report: "Report"):

        result = invocation_result_to_level_map[report.invocation_result]

        text = self.messages[result]

        text = text.format(
            task_name=report.task.name,
            invocation_time=report.invocation_datetime.strftime("%x %X"),
            n_warnings=report.n_log_warnings,
            n_errors=report.n_log_errors,
        )

        base_url = get_base_url()
        logviewer_url = reverse("log_viewer", args=(report.id,))

        blocks = [
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": "django-uwsgi-taskmanager",}],
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": text,},},
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
                    "text": ("Logs tail:\n" f"```{log_tail(report.log)}```"),
                },
            },
        ]

        # Finally, post message to channel (fail silently)
        self.client.chat_postMessage(channel=self.channel, blocks=blocks)


class EmailNotificationHandler(NotificationHandler):
    subjects: Dict[int, str] = {
        LEVEL_OK: 'Task *"{task_name}"* completed successfully.',
        LEVEL_WARNINGS: 'Task *"{task_name}"* completed with warning.',
        LEVEL_ERRORS: 'Task *"{task_name} with  errors.',
        LEVEL_FAILED: 'Task *"{task_name}"* has failed.',
    }

    def __init__(
        self,
        from_email: str,
        recipients: List[str],
        level: Union[int, str] = LEVEL_DEFAULT,
    ):

        self.from_email = from_email

        self.recipients = recipients

        super().__init__(level)

    def emit(self, report: "Report"):
        result = invocation_result_to_level_map[report.invocation_result]

        text = self.messages[result]

        text = text.format(
            task_name=report.task.name,
            invocation_time=report.invocation_datetime.strftime("%x %X"),
            n_warnings=report.n_log_warnings,
            n_errors=report.n_log_errors,
        )

        send_mail(
            subject=self.subjects[result],
            message=text,
            from_email=self.from_email,
            recipient_list=self.recipients,
            fail_silently=True,
        )
