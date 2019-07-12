"""Provides support for backwards compatibility with older versions of Django."""

# NOTE: Django 1.x url routing syntax. Remove when dropping Django 1.11 support.
try:
    from django.urls import include, path, re_path, register_converter  # noqa
except ImportError:  # pragma: no cover
    from django.conf.urls import include, url  # noqa

    path = None
    register_converter = None
    re_path = url
