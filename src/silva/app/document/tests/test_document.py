# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest


from zope.interface.verify import verifyObject
from zope.component import getUtility

from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.app.document.testing import FunctionalLayer
from silva.core.editor.testing import save_editor_text
from silva.core.services.interfaces import ICatalogService

HTML_CATALOG = """
<div>
  <h1>Example to catalog test</h1>
  <p>This is a ultimate catalog test</p>
</div>
"""

class DocumentTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_document(self):
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')

        self.assertTrue('document' in self.root.objectIds())
        document = self.root.document
        self.assertTrue(verifyObject(IDocument, document))
        self.assertNotEqual(document.get_editable(), None)
        self.assertEqual(document.get_viewable(), None)

        version = document.get_editable()
        self.assertTrue(verifyObject(IDocumentVersion, version))
        self.assertEqual(unicode(version.body), '<h1>Test Document</h1>')

        self.assertNotEqual(document.get_creation_datetime(), None)
        self.assertNotEqual(document.get_modification_datetime(), None)

    def test_cataloging(self):
        """Test that the content of the document is in the catalog.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')

        version = self.root.document.get_editable()
        save_editor_text(version.body, HTML_CATALOG, content=version)

        catalog = getUtility(ICatalogService)

        # Test appear in the title.
        results = list(catalog(fulltext='Test'))
        self.assertEqual(len(results), 1)
        result = results[0].getObject()
        self.assertEqual(result, self.root.document.get_editable())

        # Catalog appear in the body text.
        results = list(catalog(fulltext='catalog'))
        self.assertEqual(len(results), 1)
        result = results[0].getObject()
        self.assertEqual(result, self.root.document.get_editable())

    def test_indexes(self):
        """Test indexes.
        """
        # Editable, published
        assert False, 'TBD'

    def test_details(self):
        """Test details (intro, thumbnail).
        """
        assert False, 'TBD'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentTestCase))
    return suite
