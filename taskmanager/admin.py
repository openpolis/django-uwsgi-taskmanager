"""Define Django admin options for the taskmanager app."""

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.actions import delete_selected
from django.forms import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from taskmanager.models import AppCommand, Report, Task, TaskCategory
from taskmanager.utils import log_tail


def convert_to_local_dt(dt):
    """Convert datetime into local datetime, if django settings are set up to use TZ.

    Datetime fields in django store datetimes as UTC date, if the USE_TZ setting is set.
    To have the correct datetime sent to the admin,
    without using django templating system, the conversion needs to be done manually.

    :param dt: a datetime.datetime object
    :return:   a datetime.datetime object
    """
    if settings.USE_TZ and dt is not None:
        from pytz import timezone

        local_tz = timezone(settings.TIME_ZONE)
        return local_tz.normalize(dt.astimezone(local_tz))
    else:
        return dt


class ReportMixin(object):
    """
    Overrides some of the methods of the ModelAdmin.

    Provide a log_tail custom field showing the last lines of the log
    and a link to a logviewer.
    """

    @mark_safe
    def log_tail(self, obj):
        """Return the last lines of the log and a link to a logviewer."""
        n_max_lines = getattr(settings, "TASK_MANAGER_N_LINES_IN_REPORT_INLINE", 20)
        lines = "<pre>"
        lines += log_tail(obj.log, n_max_lines)
        if getattr(settings, "TASK_MANAGER_SHOW_LOGVIEWER_LINK", False):
            lines += ugettext_lazy(
                (
                    "\n\nShow the: <a href='{0}' target='_blank'>"
                    "complete log with filters</a>"
                )
            ).format(reverse("log_viewer", args=(obj.pk,)))
        lines += "</pre>"
        return lines


@admin.register(Report)
class ReportAdmin(ReportMixin, admin.ModelAdmin):
    """Admin options for reports."""

    date_hierarchy = "invocation_datetime"
    fields = readonly_fields = (
        "task",
        "invocation_result",
        "invocation_datetime",
        "log_tail",
        "n_log_errors",
        "n_log_warnings",
        "logfile",
    )
    list_display = ("task", "invocation_result", "invocation_datetime")
    list_filter = ("invocation_result",)
    ordering = ("-invocation_datetime", "-id")
    search_field = ("task__name", "task__status", "task__spooler_id")

    def has_add_permission(self, request):
        """Return False to avoid to add an object."""
        return False

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Override the default changeform_view method."""
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = False
        return super().changeform_view(request, object_id, extra_context=extra_context)


class ReportInlineFormset(BaseInlineFormSet):
    """An inline formset for related reports."""

    def __init__(self, *args, **kwargs):
        """
        Initialize the exception.

        number of reports shown is read from settings, defaults to 5 filter
        reports related to current instance, order by invocation_datetime desc,
        return last n_reports
        """
        super().__init__(*args, **kwargs)
        n_reports = getattr(settings, "TASK_MANAGER_N_REPORTS_INLINE", 5)
        self.queryset = self.model._default_manager.filter(
            **{self.fk.name: self.instance}
        ).order_by("-invocation_datetime")[:n_reports]


class ReportInline(ReportMixin, admin.TabularInline):
    """An inline for related reports."""

    extra = 0
    fields = ("invocation_result", "invocation_datetime", "log_tail")
    formset = ReportInlineFormset
    max_num = getattr(settings, "TASK_MANAGER_N_REPORTS_INLINE", 5) | 10
    model = Report
    readonly_fields = (
        "invocation_result",
        "invocation_datetime",
        "log_tail",
        "n_log_errors",
        "n_log_warnings",
    )
    show_change_link = True

    def has_add_permission(self, request):
        """Return False to avoid to add an object."""
        return False


class TaskInline(admin.TabularInline):
    """An inline for tasks, to use inside TaskCategory detail view."""

    extra = 0
    fields = readonly_fields = ("name", "arguments", "status_str")
    model = Task
    show_change_link = True

    def status_str(self, obj):
        """Return the string representation of status/last result/next ride."""
        status_str = obj.status + "/"
        last_invocation_dt = convert_to_local_dt(obj.cached_last_invocation_datetime)
        try:
            s = (
                f"{last_invocation_dt:%Y-%m-%d %H:%M:%S}: "
                f"{obj.cached_last_invocation_result} - "
                f"{obj.cached_last_invocation_n_errors}E, "
                f"{obj.cached_last_invocation_n_warnings}W"
            )
        except AttributeError:
            s = "-"
        if getattr(settings, "TASK_MANAGER_SHOW_LOGVIEWER_LINK", False):
            from django.utils.html import format_html

            if obj.last_report:
                logviewer_url = getattr(
                    settings,
                    "TASK_MANAGER_LOGVIEWER_URL",
                    f"/taskmanager/logviewer/{obj.last_report.id}",
                )
                s = format_html(f'<a href="{logviewer_url}" target="_blank">{s}</a>')
        status_str += s + "/"
        if obj.cached_next_ride:
            s = f"{convert_to_local_dt(obj.cached_next_ride):%Y-%m-%d %H:%M:%S}"
        else:
            s = "-"
        status_str += s
        return status_str

    status_str.short_description = "Status/Last result/Next ride"
    status_str.allow_tags = True


@admin.register(AppCommand)
class AppCommandAdmin(admin.ModelAdmin):
    """Admin options for application commands."""

    change_form_template = "admin/appcommand_changeform.html"
    list_display = ("app_name", "name", "active")
    list_editable = ("active",)
    list_filter = ("active",)
    ordering = ("app_name", "name")
    readonly_fields = ("app_name", "name")
    search_field = ("app_name", "name")

    def has_add_permission(self, request):
        """Return False to avoid to add an object."""
        return False

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Override the default changeform_view method."""
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = False
        return super().changeform_view(request, object_id, extra_context=extra_context)


class BulkDeleteMixin(object):
    """A mixin used within ModelAdmin extensions.

    It override the default bulk delete action with a method that invokes
    delete() on each item in the queryset.

    This can be useful whenever an overridden delete() method fo each model
    instance to be deleted should be invoked, instead of the default sql bulk
    delete shortcut used by the default action.

    See:
    https://stackoverflow.com/questions/6321940
    """

    class SafeDeleteQuerysetWrapper(object):
        """Override the queryset returned by the model's manager to intercept delete.

        Implement __iter__, __getattr__, __getitem__ and __len__ to quack like a dict,
        like django querysets do.

        Implement _safe_delete, invokink delete() on each items in the wrapped_queryset
        """

        def __init__(self, wrapped_queryset):
            """Init method."""
            self.wrapped_queryset = wrapped_queryset

        def __getattr__(self, attr):
            """Getattr method."""
            if attr == "delete":
                return self._safe_delete
            else:
                return getattr(self.wrapped_queryset, attr, None)

        def __iter__(self):
            """Yeld obj from wrapperd queryset."""
            for obj in self.wrapped_queryset:
                yield obj

        def __getitem__(self, index):
            """Get item method."""
            return self.wrapped_queryset[index]

        def __len__(self):
            """Len method."""
            return len(self.wrapped_queryset)

        def _safe_delete(self):
            """Safe delete method."""
            for obj in self.wrapped_queryset:
                obj.delete()

    def get_actions(self, request):
        """Override ModelAdmin's get_actions, replacing the `delete_selected` item."""
        actions = getattr(super(BulkDeleteMixin, self), "get_actions")(request)  # noqa
        actions["delete_selected"] = (
            BulkDeleteMixin.action_safe_bulk_delete,
            "delete_selected",
            ugettext_lazy("Delete selected %(verbose_name_plural)s"),
        )
        return actions

    def action_safe_bulk_delete(self, request, queryset):
        """Wrap the delete_selected method with the SafeDeleteQuerysetWrapper.

        That a confirmation form is presented to the user before deletion,
        and the delete() is overridden with _safe_delete()
        """
        wrapped_queryset = BulkDeleteMixin.SafeDeleteQuerysetWrapper(queryset)
        return delete_selected(self, request, wrapped_queryset)


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    """Admin options for task categories."""

    inlines = [TaskInline]
    list_display = ("name",)


@admin.register(Task)
class TaskAdmin(BulkDeleteMixin, admin.ModelAdmin):
    """Admin options for tasks.

    Use BulkDeleteMixin, in order to invoke obj.delete() for every selected tasks.
    This is needed in order to use the Task.delete method, that stops the task before
    removing the DB record.
    """

    actions = ["launch_tasks", "stop_tasks"]
    change_form_template = "admin/custom_changeform.html"
    inlines = [ReportInline]
    list_display = (
        "name",
        "arguments",
        "status",
        "repetition_str",
        "last_result_str",
        "next_ride_str",
    )
    list_filter = ("status", "cached_last_invocation_result", "category")
    ordering = ("name",)
    readonly_fields = (
        "spooler_id",
        "status",
        "cached_last_invocation_result",
        "cached_last_invocation_datetime",
        "cached_next_ride",
    )
    save_as = True
    save_on_top = True
    search_fields = ("name", "command__app_name", "command__name")

    def save_model(self, request, obj, form, change):
        """
        Override basic save model method.

        Intercept changes and stop/re-start a task whenever a relevant change
        is detected and the task is in either SPOOLED or SCHEDULED status.

        Compute cached value for next_ride, through the `get_next_ride` method
        keep last N reports only, by removing previous reports the number of
        reports to keep is specified in KEEP_LAST_N_REPORTS settings' variable
        0 means all reports are kept

        """
        if (
            change
            and len(form.changed_data)
            and any(
                (
                    f in form.changed_data
                    for f in [
                        "scheduling",
                        "arguments",
                        "repetition_period",
                        "repetition_rate",
                    ]
                )
            )
            and obj.status in [Task.STATUS_SPOOLED, Task.STATUS_SCHEDULED]
        ):
            obj.stop()
            obj.launch()

        obj.cached_next_ride = obj.get_next_ride()
        obj.keep_last_n_reports()

        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        """Determine the HttpResponse for the change_view stage."""
        if "_start-task" in request.POST:
            obj.launch()
            self.message_user(
                request, "This task was successfully launched", level=messages.SUCCESS
            )
            return HttpResponseRedirect(".")
        if "_stop-task" in request.POST:
            obj.stop()
            self.message_user(
                request, "This task was successfully stopped", level=messages.SUCCESS
            )
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def stop_tasks(self, request, queryset):
        """Remove selected tasks, stop tasks if scheduled, before removing them."""
        for obj in queryset:
            obj.stop()
        self.message_user(
            request,
            f"{len(queryset)} tasks successfully stopped",
            level=messages.SUCCESS,
        )

    stop_tasks.short_description = ugettext_lazy("Stop selected tasks")

    def launch_tasks(self, request, queryset):
        """Launch selected tasks."""
        for obj in queryset:
            obj.launch()
        self.message_user(
            request, f"{len(queryset)} tasks launched", level=messages.SUCCESS
        )

    launch_tasks.short_description = ugettext_lazy("Start selected tasks")

    def last_result_str(self, obj):
        """Return the string representation of the last result."""
        last_invocation_dt = convert_to_local_dt(obj.cached_last_invocation_datetime)
        try:
            s = (
                f"{last_invocation_dt:%Y-%m-%d %H:%M:%S}: "
                f"{obj.cached_last_invocation_result} - "
                f"{obj.cached_last_invocation_n_errors}E, "
                f"{obj.cached_last_invocation_n_warnings}W"
            )
        except (AttributeError, TypeError):
            s = "-"
        if getattr(settings, "TASK_MANAGER_SHOW_LOGVIEWER_LINK", False):
            from django.utils.html import format_html

            if obj.last_report:
                logviewer_url = getattr(
                    settings,
                    "TASK_MANAGER_LOGVIEWER_URL",
                    f"/taskmanager/logviewer/{obj.last_report.id}",
                )
                s = format_html(f'<a href="{logviewer_url}" target="_blank">{s}</a>')
        return s

    last_result_str.short_description = "Last result"
    last_result_str.allow_tags = True

    def repetition_str(self, obj):
        """Return the string representation of the repetition."""
        if obj.repetition_rate and obj.repetition_period:
            return f"{obj.repetition_rate} {obj.repetition_period}"
        else:
            return "-"

    repetition_str.short_description = "Repetition"

    def next_ride_str(self, obj):
        """Return the string representation of the next ride."""
        if obj.cached_next_ride:
            return f"{convert_to_local_dt(obj.cached_next_ride):%Y-%m-%d %H:%M:%S}"
        else:
            return "-"

    next_ride_str.short_description = "Next ride"

    class Media:
        """Task Admin asset definitions."""

        if getattr(settings, "TASK_MANAGER_USE_FILTER_COLLAPSE", False):
            js = ["/static/js/menu_filter_collapse.js"]
