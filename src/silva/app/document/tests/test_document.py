# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest


from zope.interface.verify import verifyObject
from zope.component import getUtility, queryAdapter
from zope.component import queryMultiAdapter

from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.app.document.interfaces import IDocumentDetails
from silva.app.document.testing import FunctionalLayer
from silva.core.editor.testing import save_editor_text
from silva.core.interfaces import IFeedEntry, IFeedEntryProvider
from silva.core.interfaces import IIndexEntries
from silva.core.interfaces import IPublicationWorkflow
from silva.core.references.reference import get_content_id
from silva.core.services.interfaces import ICatalogService
from silva.core.services.interfaces import IMetadataService

from Products.Silva.testing import CatalogTransaction, TestRequest, TestCase

HTML_CATALOG = """
<div>
  <h1>Example to catalog test</h1>
  <p>This is a ultimate catalog test</p>
</div>
"""

def search(**query):
    catalog = getUtility(ICatalogService)
    return map(lambda b: b.getPath(), catalog(**query))


class DocumentTestCase(TestCase):
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

    def test_fulltext(self):
        """Test document fulltext.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')
        return
        version = self.root.document.get_editable()
        self.assertItemsEqual(
            version.fulltext(),
            ['Test document'])
        version.body.save(version, TestRequest(), """
<p>
  This is some text, with <a href="#">link to the internet</a>.
</p>
""")
        self.assertItemsEqual(
            version.fulltext(),
            ['This is some text, with', 'link to the internet',
             '.', 'Test document'])

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
  <h1>Test Document</h1>
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

    def test_feeds(self):
        """When you have published document, you can have feeds out of them.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')
        factory.manage_addDocument('work', 'Work in progress')
        version = self.root.document.get_editable()
        version.body.save(version, TestRequest(), """
<h1>Test Document</h1>
<h3>Sub title</h3>
<p>This is the first story.</p>
<p>And that is the second story of the day.</p>
""")
        binding = getUtility(IMetadataService).getMetadata(version)
        binding.setValues('silva-extra', {
                'content_description': 'Test content',
                'keywords': 'test'})
        IPublicationWorkflow(self.root.document).publish()

        feed = queryMultiAdapter(
            (self.root, TestRequest()),
            IFeedEntryProvider)
        self.assertTrue(verifyObject(IFeedEntryProvider, feed))
        entries = list(feed.entries())
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].id(), 'http://localhost/root/document')

        entry = queryMultiAdapter(
            (self.root.document, TestRequest()),
            IFeedEntry)
        self.assertTrue(verifyObject(IFeedEntry, entry))
        self.assertEqual(entry.id(), 'http://localhost/root/document')
        self.assertEqual(entry.title(), 'Test Document')
        self.assertEqual(entry.url(), 'http://localhost/root/document')
        self.assertEqual(entry.authors(), ['editor'])
        self.assertEqual(entry.description(), 'Test content')
        self.assertEqual(entry.keywords(), ['test'])
        self.assertXMLEqual(
            entry.html_description(),
            "<p>This is the first story.</p>")

        self.assertIs(
            queryMultiAdapter((self.root.work, TestRequest), IFeedEntry),
            None)

    def test_details_document_without_image(self):
        """Test details, retrieve the introduction, and no thumbnail.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')
        version = self.root.document.get_editable()
        version.body.save(version, TestRequest(), """
<h1>Test Document</h1>
<h3>Sub title</h3>
<p>This is the first story.</p>
<p>And that is the second story of the day.</p>
""")

        # Query the adapter with an interface (API)
        details = queryMultiAdapter((version, TestRequest()), IDocumentDetails)
        self.assertTrue(verifyObject(IDocumentDetails, details))
        self.assertXMLEqual(
            details.get_introduction(),
            "<p>This is the first story.</p>")
        self.assertXMLEqual(
            details.get_text(),
            """
<h3>Sub title</h3>
<p>This is the first story.</p>
<p>And that is the second story of the day.</p>
""")
        self.assertEqual(
            details.get_title(),
            'Test Document')
        self.assertEqual(
            details.get_thumbnail(),
            None)

        # Query the adapter with a view (API)
        details = queryMultiAdapter((version, TestRequest()), name='details')
        self.assertTrue(verifyObject(IDocumentDetails, details))
        self.assertXMLEqual(
            details.get_introduction(),
            "<p>This is the first story.</p>")
        self.assertXMLEqual(
            details.get_text(),
            """
<h3>Sub title</h3>
<p>This is the first story.</p>
<p>And that is the second story of the day.</p>
""")
        self.assertEqual(
            details.get_title(),
            'Test Document')
        self.assertEqual(
            details.get_thumbnail(),
            None)

    def test_details_document_with_image(self):
        """Test document details with a thumbnail and no introduction.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')
        factory = self.root.manage_addProduct['Silva']
        with self.layer.open_fixture('content-listing.png') as image:
            factory.manage_addImage('listing', 'Content Listing', image)

        version = self.root.document.get_editable()
        version.body.save(version, TestRequest(), """
<h3>Sub title</h3>
<ul>
   <li>This is a list.</li>
   <li>This is an item actually.</li>
</ul>
<div class="image">
  <img alt="logo" data-silva-reference="new" data-silva-target="%s" />
</div>
""" % get_content_id(self.root.listing))

        # Query the adapter with an interface (API)
        details = queryMultiAdapter((version, TestRequest()), IDocumentDetails)
        self.assertTrue(verifyObject(IDocumentDetails, details))
        self.assertXMLEqual(
            details.get_introduction(),
            "")
        self.assertXMLEqual(
            details.get_text(),
"""
<h3>Sub title</h3>
<ul>
   <li>This is a list.</li>
   <li>This is an item actually.</li>
</ul>
<div class="image">
  <img alt="logo" height="426" width="680"
       src="http://localhost/root/listing" />
</div>
""")
        self.assertXMLEqual(
            details.get_thumbnail(),
            """
<img src="http://localhost/root/listing?thumbnail"
     width="120" height="75" class="thumbnail" />
""")

        # Query the adapter with a view (API)
        details = queryMultiAdapter((version, TestRequest()), name='details')
        self.assertTrue(verifyObject(IDocumentDetails, details))
        self.assertXMLEqual(
            details.get_introduction(),
            "")
        self.assertXMLEqual(
            details.get_text(),
"""
<h3>Sub title</h3>
<ul>
   <li>This is a list.</li>
   <li>This is an item actually.</li>
</ul>
<div class="image">
  <img alt="logo" height="426" width="680"
       src="http://localhost/root/listing" />
</div>
""")
        self.assertXMLEqual(
            details.get_thumbnail(),
            """
<img src="http://localhost/root/listing?thumbnail"
     width="120" height="75" class="thumbnail" />
""")

    def test_details_empty_document(self):
        """Test details on a document that doesn't have any text at all.
        """
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Test Document')
        version = self.root.document.get_editable()
        version.body.save(version, TestRequest(), "")
        # Query the adapter with an interface (API)
        details = queryMultiAdapter((version, TestRequest()), IDocumentDetails)
        self.assertTrue(verifyObject(IDocumentDetails, details))
        self.assertXMLEqual(details.get_introduction(), "")
        self.assertXMLEqual(details.get_text(), "")
        self.assertEqual(details.get_title(), "")
        self.assertEqual(details.get_thumbnail(), None)

        # Query the adapter with a view (API)
        details = queryMultiAdapter((version, TestRequest()), name='details')
        details = queryMultiAdapter((version, TestRequest()), IDocumentDetails)
        self.assertTrue(verifyObject(IDocumentDetails, details))
        self.assertXMLEqual(details.get_introduction(), "")
        self.assertXMLEqual(details.get_text(), "")
        self.assertEqual(details.get_title(), "")
        self.assertEqual(details.get_thumbnail(), None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentTestCase))
    return suite
