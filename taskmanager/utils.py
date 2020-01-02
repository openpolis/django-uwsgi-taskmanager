"""Define utils for the taskmanager app."""
from typing import Optional

from django.apps import apps

from taskmanager.settings import UWSGI_TASKMANAGER_BASE_URL


def log_tail(log, n_lines=10):
    """Return the last lines of a log text."""
    lines = log.split("\n")
    hidden_lines = len(lines) - n_lines
    if hidden_lines > 0:
        lines = [f"{hidden_lines} lines hidden ..."] + lines[hidden_lines:]
    return "\n".join(lines)


def get_base_url() -> Optional[str]:
    try:
        # Check if "sites" framework is available; return current site domain.
        if apps.get_app_config("sites"):
            from django.contrib.sites.models import Site
            return Site.objects.get_current().domain
    except (LookupError, ImportError):
        pass
    # Fallback to UWSGI_TASKMANAGER_BASE_URL setting value; strip protocol bit
    return UWSGI_TASKMANAGER_BASE_URL.strip("https://").strip("http://")
