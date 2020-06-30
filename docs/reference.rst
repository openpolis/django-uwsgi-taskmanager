Reference
=========

Classes and functions are documented here automatically,
extracting information from the comments in the source code.

taskmanager.models
------------------

.. automodule:: taskmanager.models

   .. rubric:: Classes

   .. autosummary::

      AppCommand
      Report
      Task
      TaskCategory

taskmanager.management.base
---------------------------

.. automodule:: taskmanager.management.base

   .. rubric:: Classes

   .. autosummary::

      LoggingBaseCommand
      NoTerminatorStreamHandler

taskmanager.logging
-------------------

.. automodule:: taskmanager.logging

   .. rubric:: Classes

   .. autosummary::

      NoTerminatorStreamHandler

taskmanager.tasks
-----------------

.. automodule:: taskmanager.tasks

.. py:function:: taskmanager.tasks.exec_command_task(curr_task, *args, **kwargs)

    Execute the command of a Task.

    :param Task curr_task: instance of the task to execute
    :param args: unnamed arguments
    :param kwargs: named arguments
