# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt


import unittest

from Products.Silva.testing import TestRequest, TestCase

from zope.component import getMultiAdapter

from silva.core.editor.transform.interfaces import ITransformerFactory
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.interfaces import IInputEditorFilter

from ..testing import FunctionalLayer


class TitleTransformerTestCase(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Document title')

    def test_render_editor(self):
        """Transform a document text for the editor. The title will be
        added to the markup.
        """
        version = self.root.document.get_editable()
        self.assertEqual(version.get_title(), 'Document title')
        factory = getMultiAdapter((version, TestRequest()),
            ITransformerFactory)
        transformer = factory(
            'body',
            version.body,
            "<p>Hello world!</p>",
            IInputEditorFilter)
        self.assertXMLEqual(
            unicode(transformer),
            """
<h1>Document title</h1>
<p>Hello world!</p>
""")

    def test_render_editor_no_title(self):
        """Transform a document text for the editor. The document has
        no title, so nothing will be added to the document.
        """
        version = self.root.document.get_editable()
        version.set_title('')
        self.assertEqual(version.get_title(), '')
        factory = getMultiAdapter((version, TestRequest()),
            ITransformerFactory)
        transformer = factory(
            'body',
            version.body,
            "<p>Hello world!</p>",
            IInputEditorFilter)
        self.assertXMLEqual(unicode(transformer), "<p>Hello world!</p>")

    def test_save_editor(self):
        """Transform a piece of text to save from the editor. The
        title will be extract from the markup and saved on the
        version.
        """
        version = self.root.document.get_editable()
        self.assertEqual(version.get_title(), 'Document title')
        factory = getMultiAdapter((version, TestRequest()),
            ITransformerFactory)
        transformer = factory(
            'body',
            version.body,
            "<h1>New title</h1><p>Hello world!</p>",
            ISaveEditorFilter)
        self.assertXMLEqual(unicode(transformer), "<p>Hello world!</p>")
        self.assertEqual(version.get_title(), 'New title')

        # If we re-transform for the editor, we have now have the new title.
        transformer = factory(
            'body',
            version.body,
            "<p>Hello world!</p>",
            IInputEditorFilter)
        self.assertXMLEqual(
            unicode(transformer),
            """
<h1>New title</h1>
<p>Hello world!</p>
""")

    def test_save_editor_no_title(self):
        """Transform a piece of text to save from the editor. The text
        has no title, the title of the document is removed.
        """
        version = self.root.document.get_editable()
        self.assertEqual(version.get_title(), 'Document title')
        factory = getMultiAdapter((version, TestRequest()),
            ITransformerFactory)
        transformer = factory(
            'body',
            version.body,
            "<p>Hello world!</p>",
            ISaveEditorFilter)
        self.assertXMLEqual(unicode(transformer), "<p>Hello world!</p>")
        self.assertEqual(version.get_title(), u'')

    def test_save_editor_multiple_title(self):
        """Transform a piece of text to save from the editor. The text
        has multiple titles, only the first one will be taken out and
        used as title for the document.
        """
        version = self.root.document.get_editable()
        self.assertEqual(version.get_title(), 'Document title')
        factory = getMultiAdapter((version, TestRequest()),
            ITransformerFactory)
        transformer = factory(
            'body',
            version.body,
            "<h1>One title</h1><h1>Two title</h1><p>Hello world!</p>",
            ISaveEditorFilter)
        self.assertXMLEqual(
            unicode(transformer),
            "<h1>Two title</h1><p>Hello world!</p>")
        self.assertEqual(version.get_title(), 'One title')

    def test_save_editor_sub_title(self):
        """Transform a piece of text to save from the editor. The text
        has no title, and only a sub title. The document title is
        removed, and the sub-title is keept in the text.
        """
        version = self.root.document.get_editable()
        self.assertEqual(version.get_title(), 'Document title')
        factory = getMultiAdapter((version, TestRequest()),
            ITransformerFactory)
        transformer = factory(
            'body',
            version.body,
            "<h2>World domination</h2><p>Hello world!</p>",
            ISaveEditorFilter)
        self.assertXMLEqual(
            unicode(transformer),
            "<h2>World domination</h2><p>Hello world!</p>")
        self.assertEqual(version.get_title(), u'')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TitleTransformerTestCase))
    return suite
