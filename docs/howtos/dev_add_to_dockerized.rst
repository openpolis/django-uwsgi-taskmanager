How to add django-uwsgi-taskmanager to a dockerized stack
---------------------------------------------------------

This documentation is for **developers**, that want to add this application to an existing django application,
within a *dockerized* stack.

The following ``docker-compose.yml`` shows parts of a stack where an API service is provided. Note the **web.command**
value, invoking the uwsgi server in the container.

That invocation generates 4 processes able to fullfill the http(s) request-response cycle, and 2 processes
checking and running processess added to the spooler.

The ``/var/lib/uwsgi`` directory is defined as a persistent volume and contains the spooler files
used by the app. This ensures that the processes keep being executed at scheduled times even after
a container's restart.

.. note::

    The yml file is partial and is only shown for illustration purposes.

.. code-block:: yaml

    version: "3.5"

    services:
      web:
        container_name: service_web
        restart: always
        image: acme/project/service:latest
        expose:
          - "8000"
        links:
          - postgres:postgres
        environment:
          - DATABASE_URL=postgis://${POSTGRES_USER}:${POSTGRES_PASS}@postgres/${POSTGRES_DB}
          - DEBUG=${DEBUG}
          ...
          - UWSGI_TASKMANAGERN_OTIFICATIONS_SLACK_TOKEN=${UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_TOKEN}
          - UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_CHANNELS=${UWSGI_TASKMANAGER_NOTIFICATIONS_SLACK_CHANNELS}
          - CI_COMMIT_SHA=${CI_COMMIT_SHA}
        volumes:
          - public:/app/public
          - uwsgi_spooler:/var/lib/uwsgi
          - weblogs:/var/log
        command: /usr/local/bin/uwsgi --socket=:8000 --master \
            --env DJANGO_SETTINGS_MODULE=config.settings
            --pythonpath=/app --module=config.wsgi --callable=application \
            --processes=4 --spooler=/var/lib/uwsgi --spooler-processes=2

      ...

    volumes:
      public:
        name: service_public
      uwsgi_spooler:
        name: service_uwsgi_spooler
      weblogs:
        name: service_weblogs

    networks:
      default:
        external:
          name: webproxy



