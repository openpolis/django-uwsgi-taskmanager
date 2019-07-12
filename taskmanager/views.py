"""Define Django views for the taskmanager app."""

from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from taskmanager.models import Report


class LogViewerView(TemplateView):
    """A template view to view a report log."""

    template_name = "log_viewer.html"

    def get_context_data(self, **kwargs):
        """Return the context data for the view."""
        context = super().get_context_data(**kwargs)
        log_level = self.request.GET.get("log_level", "ALL").lower()
        levels = ["warning", "error"]
        pk = context.get("pk", None)
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            log = _("No log for the report {pk}.").format(pk=pk)
        else:
            log_lines = report.get_log_lines()
            context["log_error"] = {
                "lines": (x for x in log_lines if "ERROR" in x),
                "n": report.n_log_errors,
            }
            context["log_warning"] = {
                "lines": (x for x in log_lines if "WARNING" in x),
                "n": report.n_log_warnings,
            }
            context["log_all"] = {"lines": log_lines, "n": report.n_log_lines}
            if log_level in levels or log_level == "all":
                log = "\n".join(context["log_" + log_level]["lines"])
            else:
                log = _("The available levels are: ERROR or WARNING")
        context["log_txt"] = log
        context["log_levels"] = levels
        context["selected_log_level"] = log_level
        return context
