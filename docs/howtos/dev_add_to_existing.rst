How to install django-uwsgi-taskmanager in an existing project
--------------------------------------------------------------
This documentation is for **developers**, that want to add this application to their django project.

.. note::

    As a pre-requisite, the project should already be served through **uWSGI**.


0.  Install the app with `pip`:

    via **PyPI**:

    .. code-block::

        pip install django-uwsgi-taskmanager

    or via **GitHub**:

    .. code-block::

        pip install git+https://github.com/openpolis/django-uwsgi-taskmanager.git

1.  Add "taskmanager" to your `INSTALLED_APPS` setting like this:

    .. code-block:: python

        INSTALLED_APPS = [
            "django.contrib.admin",
            # ...,
            "taskmanager",
        ]

2. Run ``python manage.py migrate`` to create the taskmanager tables.

3. Run ``collectcommands`` management task to create taskmanager commands [#excludecore]_:

    .. code-block:: bash

        python manage.py collectcommands --excludecore

4. Include the taskmanager URLConf in your project ``urls.py`` *(optional)* [#taskmanagerurl]_:

    .. code-block:: python

        from django.contrib import admin
        from django.urls import include, path

        urlpatterns = [
            path("admin/", admin.site.urls),
            path("taskmanager/", include("taskmanager.urls")),
        ]

5. Set parameters in your settings file as below *(optional)*:

    .. code-block:: python

        UWSGI_TASKMANAGER_N_LINES_IN_REPORT_INLINE = 10
        UWSGI_TASKMANAGER_N_REPORTS_INLINE = 3
        UWSGI_TASKMANAGER_SHOW_LOGVIEWER_LINK = True
        UWSGI_TASKMANAGER_USE_FILTER_COLLAPSE = True
        UWSGI_TASKMANAGER_SAVE_LOGFILE = False

6. Configure the notifications, following the :ref:`howto-notifications` guide *(optional)*.


.. rubric:: Footnotes
.. [#excludecore] `excludecore` ensures that core django tasks are not fetched.
.. [#taskmanagerurl] the ``/taskmanager/logviewer`` view is added to show the complete logs message.

