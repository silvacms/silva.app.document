# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.editor.testing import save_editor_text
from silva.app.document.testing import FunctionalLayer
from silva.core.interfaces import IPublicationWorkflow
from silva.core.views.tests.test_head import HEADTestCase
from silva.core.views.tests.test_head import (
    PUBLIC_HEADERS_EXPECTED, AUTH, PRIVATE_HEADERS_EXPECTED)

from Products.Silva.ftesting import public_settings


class DocumentHEADTestCase(HEADTestCase):
    layer = FunctionalLayer

    def setUp(self):
        super(DocumentHEADTestCase, self).setUp()
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Document')

    def test_document(self):
        """Verify headers.
        """
        self.check_headers('/root/document', {}, PUBLIC_HEADERS_EXPECTED)

    def test_document_auth(self):
        self.check_headers('/root/document', AUTH, PUBLIC_HEADERS_EXPECTED)

    def test_document_auth_private(self):
        self.set_private(self.root.document)
        self.check_headers('/root/document', AUTH, PRIVATE_HEADERS_EXPECTED)


class DocumentViewTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')

    def test_view(self):
        """Test document public view.
        """
        version = self.root.document.get_editable()
        save_editor_text(version.body, """
<p>This is a simple piece of text.</p>
""")
        IPublicationWorkflow(self.root.document).publish()
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/document'), 200)
            # Title should be an h1.
            self.assertEqual(browser.inspect.title, ['Test Document'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentHEADTestCase))
    suite.addTest(unittest.makeSuite(DocumentViewTestCase))
    return suite
