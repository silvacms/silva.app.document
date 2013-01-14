# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.tests.test_xml_export import SilvaXMLTestCase
from silva.app.document.testing import FunctionalLayer
from silva.core.editor.testing import save_editor_text

HTML_REFERENCE = """
<div>
  <h1>Example</h1>
  <p>
    here is a paragraph...</p>
  <p>
    then comes a <a class="link" target="_self"
    reference="{link}">link</a></p>
  <p>then comes an image :</p>
  <div class="image default">
    <img alt="location.png"
         reference="{image}" />
    <span class="image-caption">location.png</span>
  </div>
</div>
"""
HTML_MULTIPLE = """
<div>
   <h1>Hello world</h1>
   <p>This is a nice text</p>
   <img src="somewhere.gif" />
</div>
<p class="footnote">
   This is a foot that have a <i>note</i></p>.
"""

class DocumentExportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')

    def test_export_reference(self):
        """Test export of mutiple references in one document.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('other', 'Other')

        with self.layer.open_fixture('content-listing.png') as image:
            factory.manage_addImage('image', 'Image', image)

        version = self.root.folder.example.get_editable()
        save_editor_text(
            version.body, HTML_REFERENCE,
            content=version,
            image_content=self.root.folder.image,
            image_name=u'document image',
            link_content=self.root.folder.other,
            link_name=u'document link')

        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_reference.silvaxml')
        self.assertEqual(       # This is the mockup content
            exporter.getZexpPaths(),
            [(('', 'root', 'folder', 'other'), '1.zexp')])
        self.assertEqual(
            exporter.getAssetPaths(),
            [(('', 'root', 'folder', 'image'), '1')])
        self.assertEqual(
            exporter.getProblems(),
            [])

    def test_export_reference_external(self):
        """Test export of references that have targets not in the
        export tree. This should fail.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('other', 'Other')

        with self.layer.open_fixture('content-listing.png') as image:
            factory.manage_addImage('image', 'Image', image)

        version = self.root.folder.example.get_editable()
        save_editor_text(
            version.body, HTML_REFERENCE,
            content=version,
            image_content=self.root.image,
            image_name=u'document image',
            link_content=self.root.other,
            link_name=u'document link')

        self.assertExportFail(self.root.folder)

    def test_export_reference_external_force(self):
        """Test export of references that have targets not in the
        export tree, with the option external_references set to True.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('other', 'Other')

        with self.layer.open_fixture('content-listing.png') as image:
            factory.manage_addImage('image', 'Image', image)

        version = self.root.folder.example.get_editable()
        save_editor_text(
            version.body, HTML_REFERENCE,
            content=version,
            image_content=self.root.image,
            image_name=u'document image',
            link_content=self.root.other,
            link_name=u'document link')

        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_reference_external.silvaxml',
            options={'external_references': True})
        self.assertEqual(
            exporter.getZexpPaths(),
            [])
        self.assertEqual(
            exporter.getAssetPaths(),
            [])
        self.assertEqual(
            exporter.getProblems(),
            [(u'Text contains a reference pointing outside of the export (../other).', version),
             (u'Text contains a reference pointing outside of the export (../image).', version)])

    def test_export_reference_broken(self):
        """Test export of broken and missing references.
        """
        version = self.root.folder.example.get_editable()
        save_editor_text(
            version.body, HTML_REFERENCE,
            content=version,
            image_content=None,
            image_name=u'document image',
            link_content=None,
            link_name=u'document link')

        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_reference_broken.silvaxml')
        self.assertEqual(
            exporter.getZexpPaths(),
            [])
        self.assertEqual(
            exporter.getAssetPaths(),
            [])
        self.assertEqual(
            exporter.getProblems(),
            [(u'Text contains a broken reference in the export.', version),
             (u'Text contains a broken reference in the export.', version)])

    def test_export_multiple_root(self):
        """Test export of an HTML tag that have multiple root elements.
        """
        version = self.root.folder.example.get_editable()
        save_editor_text(version.body, HTML_MULTIPLE)

        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_multiple.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentExportTestCase))
    return suite
