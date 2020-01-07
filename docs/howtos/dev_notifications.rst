.. _howto-notifications:

How to enable notifications
---------------------------

To enable Slack notifications support for failing tasks, you have to first install the
required packages, which are not included by default. To do that, just:

.. code-block::

    pip install django-uwsgi-taskmanager[notifications]

This will install the ``django-uwsgi-taskmanager`` package from PyPI, including the optional slackclient_ dependency
required to make Slack notifications work.

Email notifications are instead handled using Django `django.core.mail`_
module, so no further dependencies are needed and they should work out of the box, given you have at
least one `email backend`_ properly
configured.

Then, you have to configure the following settings:

- ``UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_TOKEN``, which must be set with you own Slack token as string.
- ``UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_CHANNELS``, a list of strings representing the names or ids of the channels which will receive the notifications.
- ``UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_FROM``, the "from address" you want your outgoing notification emails to use.
- ``UWSGI_TASKMANAGER_NOTIFICATIONS_EMAIL_RECIPIENTS``, a list of strings representing the recipients of the notifications.

.. _django.core.mail: https://docs.djangoproject.com/en/2.2/topics/email/
.. _email backend: https://docs.djangoproject.com/en/2.2/topics/email/#email-backends
.. _slackclient: https://slack.dev/python-slackclient/

