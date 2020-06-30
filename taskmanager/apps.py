"""Configure taskmanager app."""
from pydoc import locate
from typing import Dict, Type

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from taskmanager.notifications import NotificationHandler
from taskmanager.settings import UWSGI_TASKMANAGER_NOTIFICATION_HANDLERS


class TaskmanagerConfig(AppConfig):
    """Task manager app configuration."""

    name = "taskmanager"
    verbose_name = _("Task manager")

    notification_handlers: Dict[str, NotificationHandler] = {}

    def _register_notification_handlers(self) -> None:
        for name, handler in UWSGI_TASKMANAGER_NOTIFICATION_HANDLERS.items():
            handler_class: Type[NotificationHandler] = locate(handler.pop("class"))
            if handler_class:
                instance = handler_class(**handler)
                if instance:
                    self.notification_handlers[name] = instance

    def ready(self) -> None:
        """Run stuff when Django starts."""
        self._register_notification_handlers()
