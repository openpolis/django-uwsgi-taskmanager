"""Define settings for the taskmanager app."""

from typing import Dict, Optional, Any

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

UWSGI_TASKMANAGER_NOTIFICATION_HANDLERS: Dict[str, Dict[str, Any]] = getattr(
    django_project_settings, "UWSGI_TASKMANAGER_NOTIFICATION_HANDLERS", {}
)
"""
Configure notification handlers.

Example:

    UWSGI_TASKMANAGER_NOTIFICATION_HANDLERS = {
        "slack": {
            "class": "taskmanager.notifications.SlackNotificationHandler",
            "level": "warnings",
            "token": "<token>",
            "channel": "id-or-name-of-channel",
        },
        "slack-all": {
            "class": "taskmanager.notifications.SlackNotificationHandler",
            "level": "ok",
            "token": "<token>",
            "channel": "id-or-name-of-channel",
        },
        "slack-failures": {
            "class": "taskmanager.notifications.SlackNotificationHandler",
            "level": "failure",
            "token": "<token>",
            "channel": "id-or-name-of-channel",
        },
        "email-failures": {
            "class": "taskmanager.notifications.EmailNotificationHandler",
            "level": "failure",
            "from": "admin@example.com",
            "recipients": ["admin@example.com",],
        },
    }

NOTE: Email feature relies on Django built-in `send_mail()`.
Thus, an email backend (e.g. SMTP) should be configured by setting these options:
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD

"""
