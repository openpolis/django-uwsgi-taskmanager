"""Define utils for the taskmanager app."""
import re
from typing import Optional

from django.apps import apps

from taskmanager.settings import UWSGI_TASKMANAGER_BASE_URL


def log_tail(log, n_lines: int = 10) -> Optional[str]:
    """Return the last lines of a log text."""
    lines = log.split("\n")
    hidden_lines = len(lines) - n_lines
    if hidden_lines > 0:
        lines = [f"{hidden_lines} lines hidden ..."] + lines[hidden_lines:]
    return "\n".join(lines)


def get_base_url() -> Optional[str]:
    """
    Obtain the base URL of the Django site.

    Tries to get the current domain using `django.contrib.sites`,
    if the `contrib` app is available.

    Else, it will try to parse the `UWSGI_TASKMANAGER_BASE_URL` setting.

    If `UWSGI_TASKMANAGER_BASE_URL`, the function will return `None`.

    :return: A string representing the base URL, or `None` if unable to get one.
    """
    tmp: Optional[str] = None

    try:
        # Check if "sites" framework is available; return current site domain.
        if apps.get_app_config("sites"):
            from django.contrib.sites.models import Site

            tmp = Site.objects.get_current().domain

    except (LookupError, ImportError):
        # Fallback to UWSGI_TASKMANAGER_BASE_URL setting value; strip protocol bit
        if UWSGI_TASKMANAGER_BASE_URL:
            tmp = re.sub(r".+://", "", UWSGI_TASKMANAGER_BASE_URL)

    return tmp
