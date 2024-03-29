##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Error Reporting Utility interfaces
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface


class IErrorReportingUtility(Interface):
    """Error Reporting Utility"""

    def raising(info, request=None):
        """
        Logs an exception.

        :param info: The exception info, as determined by :func:`sys.exc_info`.
        """


class ILocalErrorReportingUtility(Interface):
    """Local Error Reporting Utility

    This interface contains additional management functions.
    """

    def getProperties():
        """Gets the properties as dictionary.

        keep_entries, copy_to_logfile, ignored_exceptions
        """

    def setProperties(keep_entries, copy_to_zlog=1, ignored_exceptions=(),
                      RESPONSE=None):
        """Sets the properties

        keep_entries, copy_to_logfile, ignored_exceptions

        :keyword tuple ignored_exceptions: A sequence of *str* unqualified
            class names (such as ``'Unauthorized'``) that will be ignored.
            The values here will be compared with the ``__name__`` of the first
            member of the ``info`` passed to :meth:`raising`.
        """

    def getLogEntries():
        """Returns the entries in the log, most recent first."""

    def getLogEntryById(id):
        """Return LogEntry by ID"""
