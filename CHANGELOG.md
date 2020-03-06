# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unpublished]

### Changed

- configuration for custom formset of reports in task admin change form improved; first login is now visible
- javascript error corrected for dynamic tasks filter

## [2.0.4] - 2020-01-21

### Changed

- `execute` method of the `LoggingBaseCommand` class returns the output (as in BaseCommand)
- documentation link added to README


## [2.0.3] - 2020-01-11

### Changed

- test, build and publish workflows refactored and corrected

## [2.0.2] - 2020-01-11

### Changed

- publishing to pypi test and production environment splitted into two actions

## [2.0.1] - 2020-01-11

### Added

- CI github added, pushed commits are published to pypi test,
  pushed tags are published to pypi.

## [2.0.0] - 2020-01-11

### Added

- Add sphinx documentation under `docs/`, with ReadTheDocs configuration.
- Compatibility with django 3.0 added
- Settings to see log reports added to the demo project
- Implement Slack and/or email notifications for failing tasks
- Add an `extras_require` section (`notifications`) in `setup.py`
- Add an `extras_require` section (`dev`) in `setup.py`
- Add `Makefile` with development command

### Changed
- **Important**: All app settings are now prefixed "with UWSGI_TASKMANAGER_"
- Sections added to Task edit form in admin site.
- Logviewer template is now compatible with django 3 (and django 2)
- methods `has_add_permission()` signature in `admin.py`  adjusted to django 3
- Update `black` settings in the `pyproject.toml` file
- Update `flake8` and `isort` settings in `setup.cfg`
- Remove hardcoded URLs and use url reverse method
- Update and move coverage settings to `setup.cfg`

## [1.0.2] - 2019-07-23

### Added

- Add **Copyright** section in `README.md` file

### Changed

- Add the full **GNU AGPL v3** in the `LICENSE.md` file

### Fixed

- Fix broken 1.0.1 URL in `CHANGELOG.md`
- Fix TypeError in taskcategory admin

### Removed

- Remove unused code from models

## [1.0.1] - 2019-07-13

### Changed

- Rename `collect_commands` to `collectcommands`
- Add missings setps in `README.md`

### Fixed

- Fix version 1.0.0 release date in `CHANGELOG.md`
- Add missing `__init__.py` in migrations directory
- Add missing `STATIC_ROOT` in demo settings
- Add missing media directory and settings
- Fix convert to local datetime function
- Update and complete `setup.py`

## [1.0.0] - 2019-07-12

### Added

- First release


[unreleased]: https://github.com/openpolis/django-uwsgi-taskmanager/compare/v2.0.4...master
[2.0.4]: https://github.com/openpolis/django-uwsgi-taskmanager/compare/v2.0.3...v2.0.4
[2.0.3]: https://github.com/openpolis/django-uwsgi-taskmanager/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/openpolis/django-uwsgi-taskmanager/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/openpolis/django-uwsgi-taskmanager/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/openpolis/django-uwsgi-taskmanager/compare/v1.0.2...v2.0.0
[1.0.2]: https://github.com/openpolis/django-uwsgi-taskmanager/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/openpolis/django-uwsgi-taskmanager/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/openpolis/django-uwsgi-taskmanager/releases/tag/v1.0.0
