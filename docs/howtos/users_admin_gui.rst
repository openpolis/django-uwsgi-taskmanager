.. _django-admin-section:

How to manage tasks in the django admin site
--------------------------------------------

This documentation is for **users** that want to manage management tasks within the django admin site.

It is supposed that the users know the basic usage of a django admin interface,
so CRUD operations will not be descibed here.

Once you log into the admin site of your app, you'll find a **Task manager** section, where you can
manage the tasks.

In the django admin site, a **Task manager** section will appear, containing the app's views.

.. image:: /_static/images/admin_gui_1.png
  :width: 800
  :alt: The task manager section appears


Commands
^^^^^^^^

The commands to use in tasks must be collected from the hosting project's apps,
among the defined management tasks, in order to be available as
*launchable* commands.

This can be done through the ``collectcommands`` management task [#excludecore]_:

.. code-block:: bash

    python manage.py collect_commands --excludecore -v2


.. image:: /_static/images/admin_gui_2.png
  :width: 800
  :alt: The list of commands

The complete command's syntax is visible in the command details page (click on the app name in the row of the command).

.. image:: /_static/images/admin_gui_3.png
  :width: 800
  :alt: A command's syntax


Commands can be deleted. This means that in order to create tasks out of them you will need to use the ``collectcommands``
task again.

Only commands checked with the ``active`` flag will be available to generate tasks. So the best option to remove a command
and not allow users to geneate tasks out of it is to set its ``active`` status to false.

.. note::

    It is possible to generate a task starting from the ``collectcommands`` command, so that the collection of
    available commands can be launched through the django-uwsgi-taskmanager, too.


Tasks
^^^^^
``Tasks`` is the main admin view, where all the action happens.
Tasks can be listed, filtered, searched, created, modified and removed
using the standard CRUD processes available in django-admin.

.. image:: /_static/images/admin_gui_4.png
  :width: 800
  :alt: Django tasks list view, with custom bulk actions


Actions are available to have a task start or stop, both in the *list view* and in the *detail view*.


.. image:: /_static/images/admin_gui_5.png
  :width: 800
  :alt: Django task details view with custom buttons


Task structure
^^^^^^^^^^^^^^
A task has four main sections:

- **Definition**: name, command, arguments, category and note;
- **Scheduling**: time of start and repetition period and rate;
- **Last execution**: spooler id, status, last execution datetime, last result, next execution, n. of errors and warnings;
- **Reports**: Each task's execution generates a **Report**. Only the last 5 reports are kept and shown in the Task's detail view.

Defining a task
^^^^^^^^^^^^^^^

.. image:: /_static/images/admin_gui_6.png
  :width: 800
  :alt: Django definition fields

Fields in the **definition** section:

- **name**: name a task, use unique names with prefixes, to identify tasks visually

  .. note::

    It is important to understand that a command can be used multiple times in various tasks, with different arguments.
    Use different **names** and specify differences verbosely in the **note** field to let other users make the right
    choices on which task to use.

- **command**: select the command from the collected ones, in the command popup list;
- **arguments**: the command's arguments in a special syntax:

  .. note::

      Single arguments should be separated by a *comma* (","),
      while multiple values in a single argument should be separated by a blank space,

      eg: ``-f, --secondarg param1 param2, --thirdarg=pippo, --thirdarg``

- **category**: select from an existing one, or add a new one
- **note**: a descriptive note on how the command or its arguments are used


Task categories
^^^^^^^^^^^^^^^

In order to ease the search of tasks when they start to grow in numbers, a category can be assigned to each one.
The tasks list can then be filtered by category.

.. note::

    Use simple, short words as categories and try to have less than 10 categories in all,
    in order not to confuse other users.

Scheduling a task
^^^^^^^^^^^^^^^^^

.. image:: /_static/images/admin_gui_7.png
  :width: 800
  :alt: Django scheduling fields

*Scheduling* is performed through the following fields:

- **scheduling**: date and time, sets the moment in time when the task is going to be launched for the first time.
- **repetition period**: select one among *minute*, *hour*, *day*, *month*
- **repetition rate**: set an integer

To **schedule a task to start in the future only once**: set the scheduling field to a point in time in the future
and press the start button.

To **schedule a task to start in the future and run periodically**: set **both** the scheduling
field and the repetition fields, then press the start button.

To **stop a scheduled start**: press the stop button.

Reading the task's last execution status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: /_static/images/admin_gui_8.png
  :width: 800
  :alt: Django task's last execution status

The fields in this section are *read-only* and are meant to show information on the task's lat execution.

- **spooled at**: the complete path to the file in the spooler, can be useful when debugging errors,
  but it's an *internal* information and should not be needed by standard users
- **status**: can be one of:

  - ``IDLE``: the task never started or was stopped,
  - ``STARTED``: the task is currently running,
  - ``SCHEDULED``: the task is going to start for the first time in the future,
  - ``SPOOLED``: the task has been put in the spooler and is going to start again in the future

- **last datetime**: the last execution date and time
- **last result**: last execution result

  - ``OK``: correctly executed, with no warnings, nor errors
  - ``WARNINGS``: correctly executed, but contains warnings, see the report
  - ``ERRORS``: correctly executed, but contains errors, see the report
  - ``FAILED``: there was an error while execution, see the report

- **errors**: the number of errors detected in the last execution
- **warnings**: the number of warnings detected in the last execution

.. note::

    Consider that before starting for the first time, the task is being put in the spooler, so
    whenever checking the status of a task, it can happen that its status shows ``SPOOLED``, and
    after a few moments, refreshing the page, it will show ``STARTED``.

    This is perfectly normal.


Reading the task's reports
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: /_static/images/admin_gui_9.png
  :width: 800
  :alt: Django tasks reports

Once a task is finished, a report is generated and added to the **report** section. Only the last 5 reports
are left available to the users, in order to save space.

Each report contains the **result** and **invocation datetime** fields, along with the *tail* of the last 10
lines logged during execution.

Clicking on the *complete log with filters* link, a new page cotaining the log messages is opened.

.. image:: /_static/images/admin_gui_10.png
  :width: 800
  :alt: Django tasks report with log messages

The log levels (``ALL``, ``WARNING``, ``ERROR``) add as filter and clicking on them only the messages
logget at the given level will be shown.

.. note::

    The complete list of log messages is rendered on a single page. This can be problematic whenever the
    list is really long, as rendering times may be long too.

.. rubric:: Footnotes
.. [#excludecore] `excludecore` ensures that core django tasks are not fetched.
