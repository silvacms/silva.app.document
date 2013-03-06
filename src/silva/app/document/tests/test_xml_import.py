# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Acquisition import aq_chain
from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.app.document.testing import FunctionalLayer
from silva.core.editor.interfaces import ITextIndexEntries
from silva.core.interfaces import IIndexer
from silva.core.interfaces.adapters import IIndexEntries
from silva.core.references.interfaces import IReferenceService


class DocumentImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_import_document(self):
        importer = self.assertImportFile(
            'test_import_document.silvaxml',
            ['/root/document'])
        self.assertEqual(importer.getProblems(), [])
        self.assertTrue('document' in self.root.objectIds())

        document = self.root.document
        self.assertTrue(verifyObject(IDocument, document))
        self.assertNotEqual(document.get_viewable(), None)
        self.assertEqual(document.get_editable(), None)

        version = document.get_viewable()
        self.assertTrue(verifyObject(IDocumentVersion, version))
        self.assertXMLEqual(u"""<div>
            <h1>Welcome to Silva!</h1>
            <p>Welcome to Silva! This is the public view. To actually see something interesting, try adding \'/edit\' to your url (if you\'re not already editing, you can <a href="edit">click this link</a>).</p>
          </div>
          <div><p>
            I forgot to tell you that this is valid.
          </p></div>""", unicode(version.body))

    def test_import_reference(self):
        """Import a document that contains references to a link and an image.
        """
        importer = self.assertImportFile(
            'test_import_reference.silvaxml',
            ['/root/folder',
             '/root/folder/index',
             '/root/folder/example',
             '/root/folder/folder/image',
             '/root/folder/folder'])
        self.assertEqual(
            self.root.folder.objectIds(),
            ['index', 'example', 'folder'])
        self.assertEqual(
            self.root.folder.folder.objectIds(),
            ['image'])

        document = self.root.folder.example
        image = self.root.folder.folder.image
        publication = self.root.folder
        self.assertEqual(
            importer.getProblems(),
            [('Missing image file in the import: assets/1.', image)])

        self.assertTrue(verifyObject(IDocument, document))
        self.assertEqual(document.get_viewable(), None)
        self.assertNotEqual(document.get_editable(), None)

        version = document.get_editable()
        self.assertTrue(verifyObject(IDocumentVersion, version))

        service = getUtility(IReferenceService)
        references = list(service.get_references_from(version))
        by_name = {r.tags[0]: r for r in  references}

        self.assertEqual(2, len(references))
        self.assertEqual(2, len(by_name))
        link_reference = by_name['document link']
        image_reference = by_name['document image']
        self.assertEqual(link_reference.target, publication)
        self.assertEqual(aq_chain(link_reference.target), aq_chain(publication))
        self.assertEqual(image_reference.target, image)
        self.assertEqual(aq_chain(image_reference.target), aq_chain(image))

    def test_import_reference_broken(self):
        """Import a document that contains only broken references.
        """
        importer = self.assertImportFile(
            'test_import_reference_broken.silvaxml',
            ['/root/folder',
             '/root/folder/broken',
             '/root/folder/folder',])
        self.assertEqual(
            self.root.folder.objectIds(),
            ['broken', 'folder'])

        document = self.root.folder.broken
        self.assertTrue(verifyObject(IDocument, document))
        self.assertNotEqual(document.get_viewable(), None)
        self.assertEqual(document.get_editable(), None)

        version = document.get_viewable()
        self.assertTrue(verifyObject(IDocumentVersion, version))

        service = getUtility(IReferenceService)
        references = list(service.get_references_from(version))
        by_name = {r.tags[0]: r for r in  references}

        self.assertEqual(3, len(references))
        self.assertEqual(3, len(by_name))
        link_reference = by_name['document link']
        image_reference = by_name['document image']
        image_link_reference = by_name['document image link']
        self.assertEqual(link_reference.target, None)
        self.assertEqual(image_reference.target, None)
        self.assertEqual(image_link_reference.target, None)

        self.assertEqual(
            importer.getProblems(),
            [('Refering inexisting path somewhere in the import.', version),
             ('Refering inexisting path publication in the import.', version),
             ('Refering inexisting path folder/awesome_image in the import.', version)])

    def test_import_anchor(self):
        """Test importing a document that contains anchor, and check
        they are reported to the indexes.
        """
        importer = self.assertImportFile(
            'test_import_anchor.silvaxml',
            ['/root/folder',
             '/root/folder/anchor',
             '/root/folder/indexer'])
        self.assertEqual(importer.getProblems(), [])
        self.assertEqual(
            self.root.folder.objectIds(),
            ['anchor', 'indexer'])

        document = self.root.folder.anchor
        self.assertTrue(verifyObject(IDocument, document))
        self.assertNotEqual(document.get_viewable(), None)
        self.assertEqual(document.get_editable(), None)

        version = document.get_viewable()
        self.assertTrue(verifyObject(IDocumentVersion, version))

        index = ITextIndexEntries(version.body)
        self.assertTrue(verifyObject(ITextIndexEntries, index))
        self.assertEqual(len(index.entries), 2)
        self.assertEqual(
            map(lambda e: (e.anchor, e.title), index.entries),
            [('rock', 'Rock that anchor'), ('pop', 'That will pop your mind')])

        index = IIndexEntries(document)
        self.assertTrue(verifyObject(IIndexEntries, index))
        self.assertEqual(index.get_title(), 'Anchor\'s document')
        self.assertEqual(len(index.get_entries()), 2)
        self.assertEqual(
            index.get_entries(),
            [('rock', 'Rock that anchor'), ('pop', 'That will pop your mind')])

        # Verify that the entries are available in the indexer
        indexer = self.root.folder.indexer
        self.assertTrue(verifyObject(IIndexer, indexer))
        self.assertEqual(
            indexer.get_index_names(),
            ['Rock that anchor', 'That will pop your mind'])
        self.assertEqual(
            len(indexer.get_index_entry('Rock that anchor')),
            1)
        self.assertEqual(
            len(indexer.get_index_entry('That will pop your mind')),
            1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentImportTestCase))
    return suite


