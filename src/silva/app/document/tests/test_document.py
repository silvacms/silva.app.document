# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest


from zope.interface.verify import verifyObject
from zope.component import getUtility, queryAdapter

from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.app.document.testing import FunctionalLayer
from silva.core.editor.testing import save_editor_text
from silva.core.interfaces import IIndexEntries
from silva.core.interfaces import IPublicationWorkflow
from silva.core.services.interfaces import ICatalogService

from Products.Silva.testing import CatalogTransaction, TestRequest

HTML_CATALOG = """
<div>
  <h1>Example to catalog test</h1>
  <p>This is a ultimate catalog test</p>
</div>
"""

def search(**query):
    catalog = getUtility(ICatalogService)
    return map(lambda b: b.getPath(), catalog(**query))


class DocumentTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_install(self):
        """Verify that an index is created when the extension is
        installed.
        """
        index = self.root._getOb('index', None)
        self.assertNotEqual(index, None)
        self.assertTrue(verifyObject(IDocument, index))
        self.assertNotEqual(index.get_viewable(), None)
        self.assertEqual(index.get_editable(), None)
        version = index.get_viewable()
        self.assertTrue(verifyObject(IDocumentVersion, version))

    def test_document(self):
        """Test document factory.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')

        self.assertTrue('document' in self.root.objectIds())
        document = self.root.document
        self.assertTrue(verifyObject(IDocument, document))
        self.assertNotEqual(document.get_editable(), None)
        self.assertEqual(document.get_viewable(), None)

        version = document.get_editable()
        self.assertTrue(verifyObject(IDocumentVersion, version))
        self.assertEqual(unicode(version.body), '<p></p>')

        self.assertNotEqual(document.get_creation_datetime(), None)
        self.assertNotEqual(document.get_modification_datetime(), None)

    def test_catalog(self):
        """Test that the content of the document is in the catalog.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')

        version = self.root.document.get_editable()
        save_editor_text(version.body, HTML_CATALOG, content=version)

        # Test appear in the title.
        self.assertItemsEqual(
            search(fulltext='Test'),
            ['/root/document/0'])

        # Catalog appear in the body text.
        self.assertItemsEqual(
            search(fulltext='catalog'),
            ['/root/document/0'])

    def test_catalog_transaction(self):
        """Test that the content of the document is in the catalog.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['silva.app.document']
            factory.manage_addDocument('document', 'Test Document')

            version = self.root.document.get_editable()
            save_editor_text(version.body, HTML_CATALOG, content=version)

        # Test appear in the title.
        self.assertItemsEqual(
            search(fulltext='Test'),
            ['/root/document/0'])

        # Catalog appear in the body text.
        self.assertItemsEqual(
            search(fulltext='catalog'),
            ['/root/document/0'])

    def test_indexes(self):
        """Test Indexer indexes.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')
        version = self.root.document.get_editable()
        version.body.save(version, TestRequest(), """
<p>
  <a class="anchor" name="first" title="First anchor">First anchor</a>
  Some text.
  <a class="anchor" name="second" title="Second anchor">First anchor</a>
</p>
""")

        # There are no entries by default, and not published.
        indexes = queryAdapter(self.root.document, IIndexEntries)
        self.assertTrue(verifyObject(IIndexEntries, indexes))
        self.assertEqual(indexes.get_title(), '')
        self.assertEqual(indexes.get_entries(), [])

        # Published, we see the title and the entries
        IPublicationWorkflow(self.root.document).publish()
        indexes = queryAdapter(self.root.document, IIndexEntries)
        self.assertTrue(verifyObject(IIndexEntries, indexes))
        self.assertEqual(indexes.get_title(), 'Test Document')
        self.assertEqual(indexes.get_entries(), [('first', 'First anchor'),
                                                 ('second', 'Second anchor')])

    def test_details(self):
        """Test details (intro, thumbnail).
        """
        assert False, 'TBD'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentTestCase))
    return suite
