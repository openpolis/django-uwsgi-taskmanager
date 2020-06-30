.. Django uWSGI taskmanager documentation master file, created by
   sphinx-quickstart on Sun Dec 29 13:37:22 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django uWSGI taskmanager's documentation!
====================================================

uWSGI taskmanager is a Django application that can be used to launch management tasks *asynchronously*,
via the standard Django admin interface, using `uWSGI spooler`_.

The rationale for this app is to let people having access to the django admin interface,
launch or schedule management tasks, without having to consult the *developers* or *operations* teams.

The **features** include:

- start and stop tasks via the django admin interface
- schedule tasks for future executions
- program periodic tasks launch
- check, filter and download the generated log messages, watching how created live
- simply write a standard Django `Command` class (your app doesn't need to interact with Django uWSGI Taskmanager)
- get notifications via Slack, email or build a custom notification class

.. _uWSGI spooler: https://uwsgi-docs.readthedocs.io/en/latest/Spooler.html?highlight=spooler



.. image:: _static/images/dtm-show-2.gif
  :width: 800
  :alt: Animateg GIF
An animated GIF of how it all works. Click to enlarge.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   getstarted.rst
   howtos/howtos.rst
   reference.rst
   discussions.rst


