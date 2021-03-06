# coding: utf-8

"""
    unittest base
    ~~~~~~~~~~~~~

    :copyleft: 2009-2019 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import warnings

from django.test import TestCase
from django.urls import reverse

# https://github.com/jedie/django-tools
from django_tools.unittest_utils import assertments
from django_tools.unittest_utils.assertments import assert_in_dedent, assert_pformat_equal

from .BrowserDebug import debug_response


class BaseUnittestCase(TestCase):
    """
    Extensions to plain Unittest TestCase

    TODO: move all assert methods to django_tools/unittest_utils/assertments.py
    """

    maxDiff = 3000

    def assertEqual_dedent(self, first, second, msg=""):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_pformat_equal!", DeprecationWarning)
        assert_pformat_equal(first, second, msg=msg)

    def assertIn_dedent(self, member, container, msg=None):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_in_dedent!", DeprecationWarning)
        assert_in_dedent(member, container)

    def assert_is_dir(self, path):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_is_dir!", DeprecationWarning)
        assertments.assert_is_dir(path)

    def assert_not_is_dir(self, path):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_path_not_exists!", DeprecationWarning)
        assertments.assert_path_not_exists(path)

    def assert_is_file(self, path):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_is_file!", DeprecationWarning)
        assertments.assert_is_file(path)

    def assert_not_is_File(self, path):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_path_not_exists!", DeprecationWarning)
        assertments.assert_path_not_exists(path)

    def assert_startswith(self, text, prefix):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_startswith!", DeprecationWarning)
        assertments.assert_startswith(text, prefix)

    def assert_endswith(self, text, prefix):
        warnings.warn("Use django_tools.unittest_utils.assertments.assert_endswith!", DeprecationWarning)
        assertments.assert_endswith(text, prefix)

    def assert_exception_startswith(self, context_manager, text):
        """
        e.g.:

        with self.assertRaises(AssertionError) as cm:
            do_something()

        self.assert_exception_startswith(cm, "First part of the error message")
        """
        exception_text = context_manager.exception.args[0]
        if not exception_text.startswith(text):
            msg = "%r doesn't starts with %r" % (exception_text, text)
            raise self.failureException(msg)

    def get_admin_url(self, obj, suffix):
        opts = obj._meta
        change_url = reverse("admin:%s_%s_%s" % (opts.app_label, opts.model_name, suffix), args=(obj.pk,))
        return change_url

    def get_admin_change_url(self, obj):
        """
        Get the admin change url for the given model instance.
        e.g.:
            "/admin/<app_name>/<model_name>/<pk>/"
        """
        return self.get_admin_url(obj, suffix="change")

    def get_admin_add_url(self, obj):
        """
        Get the admin add url for the given model.
        e.g.:
            "/admin/<app_name>/<model_name>/add/"
        """
        opts = obj._meta
        change_url = reverse("admin:%s_%s_add" % (opts.app_label, opts.model_name))
        return change_url

    def get_messages(self, response):
        """
        Return all django message framwork entry as a normal list
        """
        return [str(message) for message in response.wsgi_request._messages]


class BaseTestCase(BaseUnittestCase):
    # Should we open a browser traceback?
    browser_traceback = True

    def raise_browser_traceback(self, response, msg):
        debug_response(response, self.browser_traceback, msg, display_tb=False)
        msg += ' (url: "%s")' % response.request.get("PATH_INFO", "???")
        raise self.failureException(msg)

    def assertStatusCode(self, response, excepted_code=200):
        """
        assert response status code, if wrong, do a browser traceback.
        """
        if response.status_code == excepted_code:
            return  # Status code is ok.
        msg = 'assertStatusCode error: "%s" != "%s"' % (response.status_code, excepted_code)
        self.raise_browser_traceback(response, msg)

    # def _assert_and_parse_html(self, html, user_msg, msg):
    #     """
    #     convert a html snippet into a DOM tree.
    #     raise error if snippet is no valid html.
    #     """
    #     try:
    #         return parse_html(html)
    #     except HTMLParseError as e:
    #         self.fail('html code is not valid: %s - code: "%s"' % (e, html))
    #
    # def _assert_and_parse_html_response(self, response):
    #     """
    #     convert html response content into a DOM tree.
    #     raise browser traceback, if content is no valid html.
    #     """
    #     try:
    #         return parse_html(response.content)
    #     except HTMLParseError as e:
    #         self.raise_browser_traceback(response, "Response's content is no valid html: %s' % e)

    def assertDOM(self, response, must_contain=(), must_not_contain=(), use_browser_traceback=True):
        """
        Asserts that html response contains 'must_contain' nodes, but no
        nodes from must_not_contain.
        """
        for txt in must_contain:
            try:
                self.assertContains(response, txt, html=True)
            except AssertionError as err:
                if use_browser_traceback:
                    self.raise_browser_traceback(response, err)
                raise

        for txt in must_not_contain:
            try:
                self.assertNotContains(response, txt, html=True)
            except AssertionError as err:
                if use_browser_traceback:
                    self.raise_browser_traceback(response, err)
                raise

    def assertMessages(self, response, messages):
        self.assertEqual(self.get_messages(response), messages)

    def assertResponse(
        self,
        response,
        must_contain=None,
        must_not_contain=None,
        status_code=200,
        template_name=None,
        messages=None,
        html=False,
        browser_traceback=True,
    ):
        """
        Check the content of the response
        must_contain - a list with string how must be exists in the response.
        must_not_contain - a list of string how should not exists.
        """
        if must_contain is not None:
            for must_contain_snippet in must_contain:
                try:
                    self.assertContains(response, must_contain_snippet, status_code=status_code, html=html)
                except AssertionError as err:
                    if browser_traceback:
                        msg = 'Text not in response: "%s": %s' % (must_contain_snippet, err)
                        debug_response(response, self.browser_traceback, msg, display_tb=True)
                    raise

        if must_not_contain is not None:
            for must_not_contain_snippet in must_not_contain:
                try:
                    self.assertNotContains(response, must_not_contain_snippet, status_code=status_code, html=html)
                except AssertionError as err:
                    if browser_traceback:
                        msg = 'Text should not be in response: "%s": %s' % (must_not_contain_snippet, err)
                        debug_response(response, self.browser_traceback, msg, display_tb=True)
                    raise

        try:
            self.assertEqual(response.status_code, status_code)
        except AssertionError as err:
            if browser_traceback:
                msg = "Wrong status code: %s" % err
                debug_response(response, self.browser_traceback, msg, display_tb=True)
            raise

        if template_name is not None:
            try:
                self.assertTemplateUsed(response, template_name=template_name)
            except AssertionError as err:
                if browser_traceback:
                    msg = "Template not used: %s" % err
                    debug_response(response, self.browser_traceback, msg, display_tb=True)
                raise

        if messages is not None:
            try:
                self.assertMessages(response, messages)
            except AssertionError as err:
                if browser_traceback:
                    msg = "Wrong messages: %s" % err
                    debug_response(response, self.browser_traceback, msg, display_tb=True)
                raise
