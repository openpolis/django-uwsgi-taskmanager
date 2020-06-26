"""Define Django urls for the taskmanager app."""

from taskmanager.compat import re_path
from taskmanager.views import LogViewerView, LiveLogViewerView, AjaxUnreadLogLines

# NOTE: Django 1.x url routing syntax.
# Update to `path('logviewer/<int:pk>', ...)` when dropping Django 1.11 support.
urlpatterns = [
    re_path(r"^logviewer/(?P<pk>[^/.]+)/", LogViewerView.as_view(), name="log_viewer"),
    re_path(r"^livelogviewer/(?P<pk>[^/.]+)/", LiveLogViewerView.as_view(), name="live_log_viewer"),
    re_path(r"^unread_loglines/(?P<pk>[^/.]+)/", AjaxUnreadLogLines.as_view(), name='ajax_unread_log_lines')
]
