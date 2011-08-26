# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Acquisition import aq_chain
from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from silva.app.document.testing import FunctionalLayer
from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.core.interfaces.events import IContentImported
from silva.core.references.interfaces import IReferenceService


class DocumentImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_import_document(self):
        self.import_file('test_import_document.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/document'],
            IContentImported)

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
        self.import_file('test_import_reference.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/index',
             'ContentImported for /root/folder/example',
             'ContentImported for /root/folder/folder/image',
             'ContentImported for /root/folder/folder',],
            IContentImported)
        self.assertEqual(
            self.root.folder.objectIds(),
            ['index', 'example', 'folder'])
        self.assertEqual(
            self.root.folder.folder.objectIds(),
            ['image'])

        document = self.root.folder.example
        image = self.root.folder.folder.image
        publication = self.root.folder
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
        self.import_file(
            'test_import_reference_broken.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/broken',
             'ContentImported for /root/folder/folder',],
            IContentImported)
        self.assertEqual(
            self.root.folder.objectIds(),
            ['broken', 'folder'])
        self.assertEqual(
            self.root.folder.folder.objectIds(),
            [])

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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentImportTestCase))
    return suite


