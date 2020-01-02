"""Define settings for the taskmanager app."""

from typing import List, Optional

from django.conf import settings as django_project_settings

UWSGI_TASKMANAGER_BASE_URL: Optional[str] = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_BASE_URL", None
)

UWSGI_TASKMANAGER_N_LINES_IN_REPORT_LOG: int = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_N_LINES_IN_REPORT_LOG", 10
)

UWSGI_TASKMANAGER_N_LINES_IN_REPORT_INLINE: int = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_N_LINES_IN_REPORT_INLINE", 20
)

UWSGI_TASKMANAGER_N_REPORTS_INLINE: int = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_N_REPORTS_INLINE", 5
)

UWSGI_TASKMANAGER_SHOW_LOGVIEWER_LINK: bool = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_SHOW_LOGVIEWER_LINK", True
)

UWSGI_TASKMANAGER_USE_FILTER_COLLAPSE: bool = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_USE_FILTER_COLLAPSE", True
)

UWSGI_TASKMANAGER_SAVE_LOGFILE: bool = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_SAVE_LOGFILE", True
)

UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_TOKEN: Optional[str] = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_TOKEN", None
)

UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_CHANNELS: List[str] = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_CHANNELS", []
)

UWSGI_TASKMANAGER_NOTIFICATIONS_FAILURE_MESSAGE: str = getattr(
    django_project_settings,
    "UWSGI_TASKMANAGER_NOTIFICATIONS_FAILURE_MESSAGE",
    'Task *"{task_name}"* invoked at {invocation_time} *failed*.',
)

UWSGI_TASKMANAGER_NOTIFICATIONS_WARNINGS_MESSAGE: str = getattr(
    django_project_settings,
    "UWSGI_TASKMANAGER_NOTIFICATIONS_WARNINGS_MESSAGE",
    'Task *"{task_name}"* invoked at {invocation_time} completed successfully '
    "with *{n_errors}* errors and *{n_warnings}* warnings.",
)

UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_FROM: str = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_FROM", None
)

UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_RECIPIENTS: List[str] = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_RECIPIENTS", []
)

# Email feature relies on Django built-in `send_mail()`.
# Thus, an email backend (e.g. SMTP) should be configured by setting these options:
# - EMAIL_HOST
# - EMAIL_PORT
# - EMAIL_HOST_USER
# - EMAIL_HOST_PASSWORD
