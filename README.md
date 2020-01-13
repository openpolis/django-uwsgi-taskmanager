# Django uWSGI Taskmanager

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Django application to manage async tasks via admin interface, using uWSGI spooler.

See documentation at http://django-uwsgi-taskmanager.rtfd.io/

## Features

- Start and stop your tasks via admin
- Schedule tasks
- Plan tasks as cron items
- Check or download the generated reports/logs
- Simply write a standard Django `Command` class (your app doesn't need to interact with Django uWSGI Taskmanager)
- Get notifications via Slack or email when a task fails

## Installation

0.  Install the app with `pip`:

    -  via PyPI:

       `pip install django-uwsgi-taskmanager`

    -  or via GitHub:

       `pip install git+https://github.com/openpolis/django-uwsgi-taskmanager.git`

1.  Add "taskmanager" to your `INSTALLED_APPS` setting like this:

    ```python
    INSTALLED_APPS = [
        "django.contrib.admin",
        # ...
        "taskmanager",
    ]
    ```

2. Run `python manage.py migrate` to create the taskmanager tables.

3. Run `python manage.py collectcommands` to create taskmanager commands.

4. Include the taskmanager URLConf in your project `urls.py` like this _(optional)_:

    ```python
    from django.contrib import admin
    from django.urls import include, path
    
    urlpatterns = [
        path("admin/", admin.site.urls),
        path("taskmanager/", include("taskmanager.urls")),
    ]
    ```

5. Set parameters in your settings file as below _(optional)_:

    ```pythonstub
    UWSGI_TASKMANAGER_N_LINES_IN_REPORT_INLINE = 10
    UWSGI_TASKMANAGER_N_REPORTS_INLINE = 3
    UWSGI_TASKMANAGER_SHOW_LOGVIEWER_LINK = True
    UWSGI_TASKMANAGER_USE_FILTER_COLLAPSE = True
    UWSGI_TASKMANAGER_SAVE_LOGFILE = False
    ```

## Usage

You just need to install `django-uwsgi-taskmanager` in your Django Project and run `collectcommands` as described.
Django uWSGI Taskmanager will collect all the commands and make them available for asynchronous scheduling in the admin.

If you need a new asynchronous task, just write a standard custom Django command, and synchronize the app. Then go to the admin page and schedule it.

You can disable some commands from the admin, and let users (with limited permissions) schedule only the available ones.

uWSGI ini file (vassal) has to include the [spooler](https://uwsgi-docs.readthedocs.io/en/latest/Spooler.html) and [pythonpath](https://uwsgi-docs.readthedocs.io/en/latest/PythonDecorators.html) option.

> **NOTE**: remember to manually create the `spooler` directory with right permissions before start uWSGI

## Enabling notifications

To enable Slack notifications support for failing tasks, you have to first install the
required packages, which are not included by default. To do that, just:

    pip install django-uwsgi-taskmanager[notifications]
    
This will install the `django-uwsgi-taskmanager` package from PyPI, including the optional dependencies
required to make Slack notifications work. 

Email notifications are instead handled using Django [`django.core.mail`](https://docs.djangoproject.com/en/2.2/topics/email/) 
module, so no further dependencies are needed and they should work out of the box, given you have at
least one [email backend](https://docs.djangoproject.com/en/2.2/topics/email/#email-backends) properly
configured.

Then, you have to configure the following settings:

- `UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_TOKEN`, which must be set with you own Slack token as string.
- `UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_CHANNELS`, a list of strings representing the names or ids of the channels which will receive the notifications.
- `UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_FROM`, the "from address" you want your outgoing notification emails to use.
- `UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_RECIPIENTS`, a list of strings representing the recipients of the notifications.

### Demo

This a basic Django demo project with a `uwsgi.ini` file and four directories (`media`, `spooler`, `static`, `venv`).

```
demo/
├── demo/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── media/
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

Collect all static files:

```bash
(venv) $ python manage.py collectstatic
```

Create all the tables:

```bash
(venv) $ python manage.py migrate
```

Collect all commands:

```bash
(venv) $ python manage.py collectcommands
```

Create a super user to login to the admin interface:

```bash
(venv) $ python manage.py createsuperuser
```

Start the project with uWSGI:

```bash
(venv) $ uwsgi --ini uwsgi.ini
```

Visit http://127.0.0.1:8000/admin/

## Copyright

**Django uWSGI taskmanager** is an application to manage async tasks via admin interface, using uWSGI spooler.

Copyright (C) 2019-2020 Gabriele Giaccari, Gabriele Lucci, Guglielmo Celata, Paolo Melchiorre

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
