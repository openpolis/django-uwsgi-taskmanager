from django.conf import settings as django_project_settings

TASK_MANAGER_N_LINES_IN_REPORT_INLINE: int = getattr(
    django_project_settings, "TASK_MANAGER_N_LINES_IN_REPORT_INLINE", 20
)

TASK_MANAGER_N_REPORTS_INLINE: int = getattr(
    django_project_settings, "TASK_MANAGER_N_REPORTS_INLINE", 5
)

TASK_MANAGER_SHOW_LOGVIEWER_LINK: bool = getattr(
    django_project_settings, "TASK_MANAGER_SHOW_LOGVIEWER_LINK", False
)

TASK_MANAGER_USE_FILTER_COLLAPSE: bool = getattr(
    django_project_settings, "TASK_MANAGER_USE_FILTER_COLLAPSE", False
)

TASK_MANAGER_SAVE_LOGFILE: bool = getattr(
    django_project_settings, "TASK_MANAGER_SAVE_LOGFILE", True
)

NOTIFICATIONS_SLACK_TOKEN: str = getattr(
    django_project_settings, "NOTIFICATIONS_SLACK_TOKEN", None
)

NOTIFICATIONS_SLACK_CHANNEL: str = getattr(
    django_project_settings, "NOTIFICATIONS_SLACK_CHANNEL", None
)

NOTIFICATIONS_FAILURE_MESSAGE: str = getattr(
    django_project_settings,
    "NOTIFICATIONS_FAILURE_MESSAGE",
    'Task *"{task_name}"* invoked at {invocation_time} failed.',
)

NOTIFICATIONS_WARNINGS_MESSAGE: str = getattr(
    django_project_settings,
    "NOTIFICATIONS_WARNINGS_MESSAGE",
    'Task *"{task_name}"* invoked at {invocation_time} completed successfully '
    "with {n_errors} errors and {n_warnings} warnings.",
)

# NOTIFICATIONS_EMAIL_RECIPIENTS: List[str]
