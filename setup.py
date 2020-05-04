"""Django uWSGI taskmanager setup."""

import os

from setuptools import find_packages, setup

import taskmanager

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    author_email="lab@openpolis.it",
    author="Gabriele Giaccari, Gabriele Lucci, Guglielmo Celata, Paolo Melchiorre",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP",
    ],
    description=taskmanager.__doc__,
    include_package_data=True,
    install_requires=[
        "django>=1.11",
        "uwsgi",
        "file-read-backwards>=2.0.0",
    ],
    extras_require={
        "notifications": ["slackclient"],
        "dev": [
            "black",
            "bump2version",
            "flake8-bugbear",
            "flake8-docstrings",
            "flake8-isort",
            "flake8",
            "isort",
            "mypy",
            "pre-commit",
        ],
        "docs": [
            "sphinx",
            "sphinx-django-command",
            "sphinx-rtd-theme",
            "sphinx-autobuild",
            "pyembed-rst"
        ]
    },
    keywords=[
        "async",
        "cron",
        "django",
        "manager",
        "spooler",
        "task",
        "timer",
        "uwsgi",
    ],
    license="AGPLv3 License",
    long_description_content_type="text/markdown",
    long_description="\n".join(
        [
            open("README.md").read(),
            open("CHANGELOG.md").read(),
            open("AUTHORS.md").read(),
            open("LICENSE.md").read(),
        ]
    ),
    name="django-uwsgi-taskmanager",
    packages=find_packages(exclude=("tests", "demo")),
    project_urls={
        "Bug Reports": "https://github.com/openpolis/django-uwsgi-taskmanager/issues",
        "Source Code": "https://github.com/openpolis/django-uwsgi-taskmanager",
    },
    python_requires="~=3.6",
    setup_requires=["wheel"],
    url="https://github.com/openpolis/django-uwsgi-taskmanager.git",
    version=taskmanager.__version__,
    zip_safe=False,
)
