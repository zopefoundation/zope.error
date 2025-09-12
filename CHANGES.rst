=========
 Changes
=========

6.0 (2025-09-12)
================

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.


5.1 (2025-02-14)
================

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.

- Specify ``python_requires`` in ``setup.py``.


5.0 (2023-07-06)
================

- Add support for Python 3.11.

- Drop support for Python 2.7, 3.5, 3.6.


4.6 (2022-08-29)
================

- Add support for Python 3.8, 3.9, 3.10.

- Drop support for Python 3.4.


4.5.0 (2018-10-19)
==================

- Add support for Python 3.7.


4.4.0 (2017-07-22)
==================

- Drop support for Python 3.3.

- Add support for Python 3.6.

- 100% test coverage.

- Remove internal ``_compat`` module in favor of ``six``, which we
  already had a dependency on.

- Stop decoding in ASCII (whatever the default codec is) in favor of UTF-8.

- Tighten the interface of
  ``ILocalErrorReportingUtility.setProperties``. Now
  ``ignored_exceptions`` is required to be str or byte objects.
  Previously any object that could be converted into a text object via
  the text constructor was accepted, but this encouraged passing class
  objects, when in actuality we need the class *name*.

- Stop ignoring ``KeyboardInterrupt`` exceptions and other similar
  ``BaseException`` exceptions during the ``raising`` method.

4.3.0 (2016-07-07)
==================

- Add support for Python 3.5.

- Drop support for Python 2.6.

- bugfix: fix leak by converting ``request.URL`` to string in
  ``ErrorReportingUtility``

4.2.0 (2014-12-27)
==================

- Add support for PyPy and PyPy3.

- Add support for Python 3.4.


4.1.1 (2014-12-22)
==================

- Enable testing on Travis.


4.1.0 (2013-02-21)
==================

- Add compatibility with Python 3.3


4.0.0 (2012-12-10)
==================

- Replace deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Drop support for Python 2.4 and 2.5.

- Sort request items for presentation in the error reporting utility.

- Don't HTML-escape HTML tracebacks twice.


3.7.4 (2012-02-01)
==================

- Add explicit tests for escaping introduced in 3.7.3.

- Handing names of classes those string representation cannot
  be determined as untrusted input thus escaping them in error reports.

- Fix tests on Python 2.4 and 2.5.

3.7.3 (2012-01-17)
==================

- Escape untrusted input before constructing HTML for error reporting.

3.7.2 (2010-10-30)
==================

- Set ``copy_to_zlog`` by default to 1/True.
  Having it turned off is a small problem, because fatal (startup) errors
  will not get logged anywhere.


3.7.1 (2010-09-25)
==================

- Add test extra to declare test dependency on ``zope.testing``.


3.7.0 (2009-09-29)
==================

- Clean up dependencies. Droped all testing dependencies as we only need
  zope.testing now.

- Fix ImportError when zope.testing is not available for some reason.

- Remove zcml slug and old zpkg-related files.

- Remove word "version" from changelog entries.

- Change package's mailing list address to zope-dev at zope.org as
  zope3-dev at zope.org is now retired. Also changed `cheeseshop` to
  `pypi` in the package's homepage url.

- Add dependency on ZODB3 as we use Persistent.

- Use a mock request for testing. Dropped the dependency on zope.publisher
  which was really only a testing dependency.

- Reduce the dependency on zope.container to one on zope.location by no
  longer using the Contained mix-in class.

3.6.0 (2009-01-31)
==================

- Use zope.container instead of zope.app.container

- Move error log bootstrapping logic (which was untested) to
  ``zope.app.appsetup``, to which we added a test.

3.5.1 (2007-09-27)
==================

- Rebump to replace faulty egg

3.5.0
=====

- Initial documented release

- Moved core components from ``zope.app.error`` to this package.
