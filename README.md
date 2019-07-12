# Django uWSGI Taskmanager

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Django application to manage async tasks via admin interface, using uWSGI spooler.

## Features

- Start and stop your tasks via admin
- Schedule tasks
- Plan tasks as cron items
- Check or download the generated reports/logs
- Simply write a standard Django Command class (your app doesn't need to interact with Django uWSGI Taskmanager)

## Installation

0.  Pip install the app:

    -  via pypi:

       `pip install django-uwsgi-taskmanager`

    -  or via github:

       `pip install git+https://github.com/openpolis/django-uwsgi-taskmanager.git`

1.  Add "taskmanager" to your `INSTALLED_APPS` setting like this:

    ```python
    INSTALLED_APPS = [
        "django.contrib.admin",
        # ...
        "taskmanager",
    ]
    ```

2. Run `python manage.py migrate` to create the taskmanager models.

3. Run `python manage.py collect_commands` to create taskmanager commands.

4. Include the taskmanager URLconf in your project `urls.py` like this _(optional)_:

    ```python
    from django.contrib import admin
    from django.urls import include, path

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("taskmanager/", include("taskmanager.urls")),
    ]
    ```

5. Set parameters in your settings file as below _(optional)_:

    ```
    TASK_MANAGER_N_LINES_IN_REPORT_INLINE = 10
    TASK_MANAGER_N_REPORTS_INLINE = 3
    TASK_MANAGER_SHOW_LOGVIEWER_LINK = True
    TASK_MANAGER_USE_FILTER_COLLAPSE = True
    TASK_MANAGER_SAVE_LOGFILE = False
    ```

## Usage

You just need to install `django-uwsgi-taskmanager` in your Django Project and run `collect_commands` as described.
Django uWSGI Taskmanager will collect all the commands and make them available for asynchronous scheduling in the admin.

If you need a new asynchronous task, just write a standard custom Django command, and synchronize the app. Then go to the admin page and schedule it.

You can disable some commands from the admin, and let users (with limited permissions) schedule only the available ones.

uWSGI ini file (vassal) has to include the [spooler](https://uwsgi-docs.readthedocs.io/en/latest/Spooler.html) and [pythonpath](https://uwsgi-docs.readthedocs.io/en/latest/PythonDecorators.html) option.

> **NOTE**: remember to manually create the `spooler` directory with right permissions before start uWSGI

### Demo

This a basic Django demo project with a `uwsgi.ini` file and three directories (`spooler`, `static`, `venv`).

```bash
demo/
├── demo/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── spooler/
├── static/
├── uwsgi.ini
└── venv/
```

This is the content of `uwsgi.ini` file required to execute the project with Django:

```ini
[uwsgi]
chdir = %d
env = DJANGO_SETTINGS_MODULE=demo.settings
http-socket = :8000
master = true
module = demo.wsgi
plugin = python3
pythonpath = %d
spooler = %dspooler
static-map = /static/=%dstatic
virtualenv = %dvenv
```

#### Try the demo project

Enter the demo directory, then create and activate the demo virtual environments:

```bash
$ cd demo
$ mkdir -p venv
$ python3 -m venv ./venv
$ source ./venv/bin/activate
```

Install Django uWSGI taskmanager:

```bash
(venv) $ pip install django-uwsgi-taskmanager
```

Install uWSGI (if you use uWSGI of your OS you can skip this step):

```bash
(venv) $ pip install uwsgi
```

Start the project with uWSGI:

```bash
(venv) $  uwsgi --ini uwsgi.ini
```
