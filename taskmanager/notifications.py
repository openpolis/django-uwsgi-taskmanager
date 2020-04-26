from abc import ABC

from taskmanager.models import Report


class Notifications:
    """
    A registry for notification handlers
    """


class NotificationHandler(ABC):
    messages = {
        Report.RESULT_OK: f"",
        Report.RESULT_ERRORS: f"",
        Report.RESULT_WARNINGS: f"",
    }

    def emit(self):
        raise NotImplementedError


#
# class SlackNotificationHandler(NotificationHandler):
#     def emit(self):
#         slack_client = slack.WebClient(
#             token=UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_TOKEN
#         )
#         blocks = [
#             {
#                 "type": "context",
#                 "elements": [{"type": "mrkdwn", "text": f"django-uwsgi-taskmanager"}],
#             }
#         ]
#         if self.invocation_result == self.RESULT_FAILED:
#             blocks.append(
#                 {
#                     "type": "section",
#                     "text": {
#                         "type": "mrkdwn",
#                         "text": UWSGI_TASKMANAGER_NOTIFICATIONS_FAILURE_MESSAGE.format(
#                             task_name=self.task.name,
#                             invocation_time=(
#                                 "<!date"
#                                 f"^{int(self.invocation_datetime.timestamp())}"
#                                 "^{date_num} {time_secs}|???>"
#                             ),
#                         ),
#                     },
#                 }
#             )
#         else:
#             blocks.append(
#                 {
#                     "type": "section",
#                     "text": {
#                         "type": "mrkdwn",
#                         "text": UWSGI_TASKMANAGER_NOTIFICATIONS_WARNINGS_MESSAGE.format(
#                             task_name=self.task.name,
#                             invocation_time=(
#                                 "<!date"
#                                 f"^{int(self.invocation_datetime.timestamp())}"
#                                 "^{date_num} {time_secs}|???>"
#                             ),
#                             n_errors=self.n_log_errors,
#                             n_warnings=self.n_log_warnings,
#                         ),
#                     },
#                 }
#             )
#         blocks.append(
#             {
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": f"Logs tail:\n ```{log_tail(self.log)}```",
#                 },
#             }
#         )
#         base_url = get_base_url()
#         if base_url:
#             logviewer_url = reverse("log_viewer", args=(self.id,))
#             blocks.append(
#                 {
#                     "type": "context",
#                     "elements": [
#                         {
#                             "type": "mrkdwn",
#                             "text": f"<http://{base_url}{logviewer_url}|Full logs>",
#                         }
#                     ],
#                 }
#             )
#         for channel in UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_CHANNELS:
#             slack_client.chat_postMessage(channel=channel, blocks=blocks)
#             # Fail silently
#
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
