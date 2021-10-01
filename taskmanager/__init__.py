"""Django application to manage async tasks via admin interface, using uWSGI spooler."""

# PEP 440 - version number format
VERSION = (2, 2, 13)

# PEP 396 - module version variable
__version__ = ".".join(map(str, VERSION))

default_app_config = "taskmanager.apps.TaskmanagerConfig"
