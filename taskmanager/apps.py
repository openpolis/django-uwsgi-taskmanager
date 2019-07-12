"""Configure taskmanager app."""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TaskmanagerConfig(AppConfig):
    """Task manager app configuration."""

    name = "taskmanager"
    verbose_name = _("Task manager")
