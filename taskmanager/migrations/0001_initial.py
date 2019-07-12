import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AppCommand",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("app_name", models.CharField(max_length=100)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("app_name", "name"),
                "verbose_name": "Command",
                "verbose_name_plural": "Commands",
            },
        ),
        migrations.CreateModel(
            name="TaskCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name": "Task category",
                "verbose_name_plural": "Tasks categories",
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "arguments",
                    models.TextField(
                        blank=True,
                        help_text=(
                            "Separate arguments with a comma ',' and parameters "
                            "with a blank space ' '. eg: -f, --secondarg "
                            "param1 param2, --thirdarg=pippo, --thirdarg"
                        ),
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("idle", "IDLE"),
                            ("spooled", "SPOOLED"),
                            ("scheduled", "SCHEDULED"),
                            ("started", "STARTED"),
                        ],
                        default="idle",
                        editable=False,
                        max_length=20,
                    ),
                ),
                ("scheduling", models.DateTimeField(blank=True, null=True)),
                (
                    "spooler_id",
                    models.FilePathField(
                        blank=True,
                        match="uwsgi_spoolfile_on_*",
                        max_length=255,
                        path="/",
                        recursive=True,
                    ),
                ),
                (
                    "command",
                    models.ForeignKey(
                        limit_choices_to={"active": True},
                        on_delete=django.db.models.deletion.CASCADE,
                        to="taskmanager.AppCommand",
                    ),
                ),
                (
                    "repetition_period",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("minute", "MINUTE"),
                            ("hour", "HOUR"),
                            ("day", "DAY"),
                            ("month", "MONTH"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "repetition_rate",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "cached_last_invocation_datetime",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Last datetime"
                    ),
                ),
                (
                    "cached_last_invocation_result",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "---"),
                            ("ok", "OK"),
                            ("failed", "FAILED"),
                            ("errors", "ERRORS"),
                            ("warnings", "WARNINGS"),
                        ],
                        max_length=20,
                        null=True,
                        verbose_name="Last result",
                    ),
                ),
                (
                    "cached_next_ride",
                    models.DateTimeField(blank=True, null=True, verbose_name="Next"),
                ),
                (
                    "cached_last_invocation_n_errors",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Errors"
                    ),
                ),
                (
                    "cached_last_invocation_n_warnings",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Warnings"
                    ),
                ),
                (
                    "note",
                    models.TextField(
                        blank=True,
                        help_text="A note on how this task is used.",
                        null=True,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose a category for this task",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="taskmanager.TaskCategory",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Task",
                "verbose_name_plural": "Tasks",
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "invocation_result",
                    models.CharField(
                        choices=[
                            ("", "---"),
                            ("ok", "OK"),
                            ("failed", "FAILED"),
                            ("errors", "ERRORS"),
                            ("warnings", "WARNINGS"),
                        ],
                        default="",
                        max_length=20,
                    ),
                ),
                ("invocation_datetime", models.DateTimeField(auto_now_add=True)),
                ("log", models.TextField(blank=True)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="taskmanager.Task",
                    ),
                ),
                ("n_log_errors", models.PositiveIntegerField(blank=True, null=True)),
                ("n_log_lines", models.PositiveIntegerField(blank=True, null=True)),
                ("n_log_warnings", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "logfile",
                    models.FilePathField(
                        blank=True,
                        default="",
                        match="*.log",
                        max_length=4096,
                        path="/",
                        recursive=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-invocation_datetime", "-id"),
                "verbose_name": "Report",
                "verbose_name_plural": "Reports",
            },
        ),
    ]
