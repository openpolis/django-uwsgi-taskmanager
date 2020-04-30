from abc import ABC
from dataclasses import dataclass
from typing import Dict, Union


try:
    import slack

except ImportError:  # pragma: no cover
    slack = None


class Notifications:
    """
    A registry for notification handlers
    """


@dataclass
class NotificationContext:
    task_name: str
    invocation_time: int
    n_warnings: int
    n_errors: int


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
        LEVEL_OK: "",
        LEVEL_WARNINGS: "",
        LEVEL_ERRORS: "",
        LEVEL_FAILED: "",
    }
    level: int

    def __init__(self, level: Union[int, str] = LEVEL_DEFAULT):
        if isinstance(level, int):
            self.level = level
        elif isinstance(level, str):
            self.level = invocation_result_to_level_map.get(level, LEVEL_OK)

    def emit(self, context: NotificationContext):
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

    def emit(self, context: NotificationContext):
        pass    # TODO: re-factor code below
        # blocks = [
        #     {
        #         "type": "context",
        #         "elements": [{"type": "mrkdwn", "text": f"django-uwsgi-taskmanager"}],
        #     }
        # ]
        # if self.invocation_result == self.RESULT_FAILED:
        #     blocks.append(
        #         {
        #             "type": "section",
        #             "text": {
        #                 "type": "mrkdwn",
        #                 "text": UWSGI_TASKMANAGER_NOTIFICATIONS_FAILURE_MESSAGE.format(
        #                     task_name=self.task.name,
        #                     invocation_time=(
        #                         "<!date"
        #                         f"^{int(self.invocation_datetime.timestamp())}"
        #                         "^{date_num} {time_secs}|???>"
        #                     ),
        #                 ),
        #             },
        #         }
        #     )
        # else:
        #     blocks.append(
        #         {
        #             "type": "section",
        #             "text": {
        #                 "type": "mrkdwn",
        #                 "text": UWSGI_TASKMANAGER_NOTIFICATIONS_WARNINGS_MESSAGE.format(
        #                     task_name=self.task.name,
        #                     invocation_time=(
        #                         "<!date"
        #                         f"^{int(self.invocation_datetime.timestamp())}"
        #                         "^{date_num} {time_secs}|???>"
        #                     ),
        #                     n_errors=self.n_log_errors,
        #                     n_warnings=self.n_log_warnings,
        #                 ),
        #             },
        #         }
        #     )
        # blocks.append(
        #     {
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn",
        #             "text": f"Logs tail:\n ```{log_tail(self.log)}```",
        #         },
        #     }
        # )
        # base_url = get_base_url()
        # if base_url:
        #     logviewer_url = reverse("log_viewer", args=(self.id,))
        #     blocks.append(
        #         {
        #             "type": "context",
        #             "elements": [
        #                 {
        #                     "type": "mrkdwn",
        #                     "text": f"<http://{base_url}{logviewer_url}|Full logs>",
        #                 }
        #             ],
        #         }
        #     )
        # for channel in UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_CHANNELS:
        #     slack_client.chat_postMessage(channel=channel, blocks=blocks)
        #     # Fail silently


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
