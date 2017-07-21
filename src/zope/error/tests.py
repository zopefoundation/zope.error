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
"""Error Reporting Utility Tests
"""
import io
import sys
import unittest
import logging

from six import text_type

from zope.exceptions.exceptionformatter import format_exception
from zope.testing import cleanup

from zope.error.error import ErrorReportingUtility, getFormattedException


class StringIO(io.BytesIO if str is bytes else io.StringIO):
    pass


class Error(Exception):

    def __init__(self, value):
        super(Error, self).__init__()
        self.value = value

    def __str__(self):
        return self.value


def getAnErrorInfo(value=""):
    try:
        raise Error(value)
    except Error:
        return sys.exc_info()


class TestRequest(object):
    """Mock request that mimics the zope.publisher request."""

    principal = None
    URL = None

    def __init__(self, environ=None):
        self._environ = environ or {}
        self._items = []

    def setPrincipal(self, principal):
        self.principal = principal

    def items(self):
        return self._items

    def getURL(self):
        return self._environ['PATH_INFO']


class URLGetter(object):

    __slots__ = ("__request",)

    def __init__(self, request):
        self.__request = request

    def __str__(self):
        return self.__request.getURL()


class ErrorReportingUtilityTests(cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super(ErrorReportingUtilityTests, self).setUp()
        self.log_buffer = StringIO()
        self.log_handler = logging.StreamHandler(self.log_buffer)
        logging.getLogger().addHandler(self.log_handler)

    def tearDown(self):
        logging.getLogger().removeHandler(self.log_handler)
        super(ErrorReportingUtilityTests, self).tearDown()

    def makeOne(self):
        return ErrorReportingUtility()

    def test_checkForEmptyLog(self):
        # Test Check Empty Log
        errUtility = self.makeOne()
        getProp = errUtility.getLogEntries()
        self.assertFalse(getProp)

    def test_checkProperties(self):
        # Test Properties test
        errUtility = self.makeOne()
        setProp = {
            'keep_entries': 10,
            'copy_to_zlog': 1,
            'ignored_exceptions': ()
            }
        errUtility.setProperties(**setProp)
        getProp = errUtility.getProperties()
        self.assertEqual(setProp, getProp)

    def test_ErrorLog(self):
        # Test for Logging Error.  Create one error and check whether its
        # logged or not.
        errUtility = self.makeOne()
        exc_info = getAnErrorInfo()
        errUtility.raising(exc_info)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        tb_text = ''.join(format_exception(as_html=0, *exc_info))

        err_id = getErrLog[0]['id']
        self.assertEqual(tb_text,
                         errUtility.getLogEntryById(err_id)['tb_text'])

    def test_ErrorLog_unicode(self):
        # Emulate a unicode url, it gets encoded to utf-8 before it's passed
        # to the request. Also add some unicode field to the request's
        # environment and make the principal's title unicode.
        request = TestRequest(environ={'PATH_INFO': '/\xd1\x82',
                                       'SOME_UNICODE': u'\u0441'})
        class PrincipalStub(object):
            id = u'\u0441'
            title = u'\u0441'
            description = u'\u0441'
        request.setPrincipal(PrincipalStub())

        errUtility = self.makeOne()
        exc_info = getAnErrorInfo(u"Error (\u0441)")
        errUtility.raising(exc_info, request=request)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        tb_text = getFormattedException(exc_info)

        err_id = getErrLog[0]['id']
        self.assertEqual(tb_text,
                         errUtility.getLogEntryById(err_id)['tb_text'])

        username = getErrLog[0]['username']
        self.assertEqual(username, u'unauthenticated, \u0441, \u0441, \u0441')

    def test_ErrorLog_url(self):
        # We want a string for the URL in the error log, nothing else
        request = TestRequest(environ={'PATH_INFO': '/foobar'})
        # set request.URL as zope.publisher would
        request.URL = URLGetter(request)

        errUtility = self.makeOne()
        exc_info = getAnErrorInfo(u"Error")
        errUtility.raising(exc_info, request=request)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        url = getErrLog[0]['url']
        self.assertIsInstance(url, str)

    def test_ErrorLog_nonascii(self):
        # Emulate a unicode url, it gets encoded to utf-8 before it's passed
        # to the request. Also add some unicode field to the request's
        # environment and make the principal's title unicode.
        request = TestRequest(environ={'PATH_INFO': '/\xd1\x82',
                                       'SOME_NONASCII': '\xe1'})
        class PrincipalStub(object):
            id = b'\xe1'
            title = b'\xe1'
            description = b'\xe1'
        request.setPrincipal(PrincipalStub())

        errUtility = self.makeOne()
        exc_info = getAnErrorInfo("Error (\xe1)")
        errUtility.raising(exc_info, request=request)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        tb_text = getFormattedException(exc_info)

        err_id = getErrLog[0]['id']
        self.assertEqual(tb_text,
                         errUtility.getLogEntryById(err_id)['tb_text'])

        username = getErrLog[0]['username']
        self.assertEqual(username, r"unauthenticated, \xe1, \xe1, \xe1")

    def test_getLogEntryById_not_found(self):
        errUtility = self.makeOne()
        self.assertIsNone(errUtility.getLogEntryById('no such id'))

    def test_getLogin_error(self):
        class PrincipalStub(object):
            id = 'id'
            title = 'title'
            description = 'description'
            def getLogin(self):
                raise Exception()
        request = TestRequest()
        request.setPrincipal(PrincipalStub())

        errUtility = self.makeOne()
        exc_info = getAnErrorInfo("Error")
        errUtility.raising(exc_info, request=request)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        username = getErrLog[0]['username']
        self.assertEqual(username,
                         u'&lt;error getting login&gt;, id, title, description')

    def test_request_items(self):
        request = TestRequest()
        request.items().append(('request&key', '<request&value>'))

        errUtility = self.makeOne()
        exc_info = getAnErrorInfo("Error")
        errUtility.raising(exc_info, request=request)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        req_html = getErrLog[0]['req_html']
        self.assertEqual(req_html, u'request&amp;key: &lt;request&amp;value&gt;<br />\n')

    def test_request_items_bytes(self):
        request = TestRequest()
        request.items().append((b'request&key', b'<request&value\xe1>'))

        errUtility = self.makeOne()
        exc_info = getAnErrorInfo(b"Error")
        errUtility.raising(exc_info, request=request)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        req_html = getErrLog[0]['req_html']
        self.assertEqual(req_html, u'request&amp;key: &lt;request&amp;value\\xe1&gt;<br />\n')

    def test_request_items_int(self):
        request = TestRequest()
        request.items().append((b'request&key', 1))

        errUtility = self.makeOne()
        exc_info = getAnErrorInfo(b"Error")
        errUtility.raising(exc_info, request=request)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        req_html = getErrLog[0]['req_html']
        self.assertEqual(req_html, u'request&amp;key: 1<br />\n')


    def test_default_ignored_exception(self):
        class Unauthorized(Exception):
            pass

        errUtility = self.makeOne()
        exc_info = (Unauthorized, None, None)
        errUtility.raising(exc_info)

        getErrLog = errUtility.getLogEntries()
        self.assertEqual(0, len(getErrLog))

    def test_tb_preformatted(self):
        errUtility = self.makeOne()
        exc_info = getAnErrorInfo("Error")

        errUtility.raising((exc_info[0], exc_info[1], 'a string tb'))

        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        self.assertIsNone(getErrLog[0]['tb_html'])
        self.assertEqual(u'a string tb', getErrLog[0]['tb_text'])


    def test_tb_preformatted_bytes(self):
        errUtility = self.makeOne()
        exc_info = getAnErrorInfo("Error")

        errUtility.raising((exc_info[0], exc_info[1], b'a string tb \xe1'))

        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        self.assertIsNone(getErrLog[0]['tb_html'])
        self.assertEqual(u'a string tb \\xe1', getErrLog[0]['tb_text'])

    def test_cleanup(self):
        errUtility = self.makeOne()
        errUtility.keep_entries = 1

        exc_info = getAnErrorInfo("Error 1")
        errUtility.raising(exc_info)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        exc_info = getAnErrorInfo("Error 2")
        errUtility.raising(exc_info)
        getErrLog = errUtility.getLogEntries()
        self.assertEqual(1, len(getErrLog))

        self.assertEqual('Error 2', getErrLog[0]['value'])


class RootErrorReportingUtilityTests(ErrorReportingUtilityTests):

    def makeOne(self):
        from zope.error.error import globalErrorReportingUtility
        return globalErrorReportingUtility

class GetPrintableTests(unittest.TestCase):
    """Testing .error.getPrintable(value)"""

    def getPrintable(self, value):
        from zope.error.error import getPrintable
        return getPrintable(value)

    def test_xml_tags_get_escaped(self):
        self.assertEqual(u'&lt;script&gt;', self.getPrintable(u'<script>'))

    def test_byte_values_get_converted_to_unicode(self):
        # This one isn't much of a test because it's the literal bytes
        # '\', 'u', '0', etc.
        self.assertEqual(u'\\u0441', self.getPrintable(br'\u0441'))
        self.assertIsInstance(self.getPrintable(br'\u0441'), text_type)

        # This is a bit better because it can't be encoded in UTF-8
        self.assertEqual(u'\\xe1', self.getPrintable(b'\xe1'))
        self.assertIsInstance(self.getPrintable(b'\xe1'), text_type)

    def test_non_str_values_get_converted_using_a_str_call(self):
        class NonStr(object):
            def __str__(self):
                return 'non-str'
        self.assertEqual(u'non-str', self.getPrintable(NonStr()))
        self.assertIsInstance(self.getPrintable(NonStr()), text_type)

    def test_non_str_those_conversion_fails_are_returned_specially(self):
        class NonStr(object):
            def __str__(self):
                raise ValueError('non-str')
        self.assertEqual(u'<unprintable NonStr object>',
                         self.getPrintable(NonStr()))
        self.assertIsInstance(self.getPrintable(NonStr()), text_type)

    def test_non_str_those_conversion_fails_are_returned_with_escaped_name(
            self):
        class NonStr(object):
            def __str__(self):
                raise ValueError('non-str')
        NonStr.__name__ = '<script>'
        self.assertEqual(u'<unprintable &lt;script&gt; object>',
                         self.getPrintable(NonStr()))

    def test_getFormattedException(self):
        try:
            raise Exception('<boom>')
        except Exception:
            self.assertIn("Exception: &lt;boom&gt;",
                          getFormattedException(sys.exc_info()))
        else: # pragma: no cover
            self.fail("Exception was not raised (should never happen)")

    def test_getFormattedException_as_html(self):
        try:
            raise Exception('<boom>')
        except Exception:
            fe = getFormattedException(sys.exc_info(), as_html=True)
            self.assertIn("<p>Traceback (most recent call last):</p>", fe)
            self.assertIn("</ul><p>Exception: &lt;boom&gt;<br />", fe)
            self.assertIn("</p><br />", fe)
        else: # pragma: no cover
            self.fail("Exception was not raised (should never happen)")

        # If this fails because you get '&lt;br /&gt;' instead of '<br />' at
        # the end of the penultimate line, you need zope.exceptions 4.0.3 with
        # the bugfix for that.


    def setUp(self):
        super(GetPrintableTests, self).setUp()
        self.log_buffer = StringIO()
        self.log_handler = logging.StreamHandler(self.log_buffer)
        logging.getLogger().addHandler(self.log_handler)

    def tearDown(self):
        logging.getLogger().removeHandler(self.log_handler)
        super(GetPrintableTests, self).tearDown()


class TestErrorHandler(unittest.TestCase):

    def test_round_trip(self):
        # We don't round trip.

        text = b'\xe1'.decode('ascii', errors="zope.error.printedreplace")
        self.assertEqual(text, u"\\xe1")
        self.assertIsInstance(text, text_type)

        # Note that this is *NOT* what we actually started with.
        # The error handler is never even invoked. It seems that
        # all of Python's built-in encodings can successfully encode
        # ascii-range characters without error
        byte = text.encode('ascii', errors="zope.error.printedreplace")
        self.assertIsInstance(byte, bytes)
        self.assertEqual(byte, b'\\xe1')

        # If we do start with  a character outside the ascii range, our
        # handler is invoked and once again escapes.
        byte = u'\xe1'.encode("ascii", errors="zope.error.printedreplace")
        self.assertIsInstance(byte, bytes)
        self.assertEqual(byte, b'\\xe1')


def test_suite():
    return unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ])
