import unittest
import lxml.etree

from zope.component import getUtility, getMultiAdapter
from zope.publisher.browser import TestRequest

from Products.Silva.tests.helpers import open_test_file
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import get_content_id
from silva.app.document.testing import FunctionalLayer
from silva.app.document.silvaxml import NS_URI as DOC_NS
from silva.core.editor.transform.silvaxml import NS_URI as EDITOR_NS
from silva.core.editor.transform.interfaces import (
    ITransformer, ISaveEditorFilter)
from Products.Silva.silvaxml.xmlexport import exportToString


class TestExportReferences(unittest.TestCase):
    layer = FunctionalLayer
    html = """
<div>
  <h1>Example</h1>
  <p>
    here is a paragraph...</p>
  <p>
    then comes a <a class="link" target="_self"
    reference="93094ba8-70bd-11e0-b805-c42c0338b1a2">link</a></p>
  <p>then comes an image :</p>
  <div class="image default">
    <img alt="location.png"
         reference="a5c84b4a-70bd-11e0-8c0a-c42c0338b1a2" />
    <span class="image-caption">location.png</span>
  </div>
</div>
"""

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')
        self.content = self.root.example
        self.version = self.content.get_editable()
        self.version.body.save_raw_text(self.html)

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['Silva']

        factory.manage_addMockupVersionedContent('other', 'Other')
        self.other = self.root.folder.other

        afile = open_test_file('content-listing.png', globals())
        try:
            factory.manage_addImage('img', 'Image', afile)
        finally:
            afile.close()
        self.image = self.root.folder.img

        reference_service = getUtility(IReferenceService)
        reference = reference_service.get_reference(
            self.version, name=u"93094ba8-70bd-11e0-b805-c42c0338b1a2",
            add=True)
        reference.set_target_id(get_content_id(self.other))
        reference = reference_service.get_reference(
            self.version, name=u"a5c84b4a-70bd-11e0-8c0a-c42c0338b1a2",
            add=True)
        reference.set_target_id(get_content_id(self.image))

    def test_export_from_root(self):
        xml_string, _ = exportToString(self.root)
        tree = lxml.etree.fromstring(xml_string)
        # from infrae.testing.xmlindent import XMLSoup
        # print XMLSoup(xml_string.strip()).prettify()

        nodes = tree.xpath('//sad:document[@id="example"]',
                            namespaces={'sad': DOC_NS})
        self.assertEquals(1, len(nodes))
        doc = nodes[0]

        nodes = doc.xpath("//ed:a[@reference]", namespaces={'ed': EDITOR_NS})
        self.assertEqual(1, len(nodes))
        node = nodes[0]
        self.assertEquals('folder/other', node.attrib['reference'])

        nodes = doc.xpath("//ed:img[@reference]", namespaces={'ed': EDITOR_NS})
        self.assertEqual(1, len(nodes))
        node = nodes[0]
        self.assertEquals('folder/img', node.attrib['reference'])


class TestExportCodeSources(unittest.TestCase):
    layer = FunctionalLayer

    html = u"""
<div>
    <p>some paragraph..</p>
    <div class="external-source default"
         data-silva-name="cs_citation"
         data-silva-settings="field_citation=blahblahblah&amp;field_author=ouam&amp;field_source=wikipedia">
    </div>
</div>
"""

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')
        self.content = self.root.example
        self.version = self.content.get_editable()
        transformer = getMultiAdapter(
            (self.version, TestRequest()), ITransformer)
        self.version.body.save_raw_text(transformer.data(
            'body',
            self.version.body,
            self.html,
            ISaveEditorFilter))

    def test_export(self):
        xml_string, _ = exportToString(self.root)
        tree = lxml.etree.fromstring(xml_string)
        print lxml.etree.tostring(tree, pretty_print=True)
        ns = {'e': "http://infrae.com/namespace/silva.core.editor",
            'cs': "http://infrae.com/namespace/Products.SilvaExternalSources"}
        sel = '//e:div[contains(@class, "external-source")]'
        nodes = tree.xpath(sel, namespaces=ns)
        self.assertEquals(1, len(nodes))
        source = nodes[0]
        self.assertEquals('cs_citation', source.attrib['source-path'])
        fields = source.xpath('./cs:fields/cs:field', namespaces=ns)
        self.assertEquals(3, len(fields))
        info = {}
        for field in fields:
            info[field.attrib['id']] = field.text
        self.assertEquals(
            set(['field-author', 'field-citation', 'field-source']),
            set(info.keys()))
        self.assertEquals('blahblahblah', info['field-citation'])
        self.assertEquals('ouam', info['field-author'])
        self.assertEquals('wikipedia', info['field-source'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestExportReferences))
    suite.addTest(unittest.makeSuite(TestExportCodeSources))
    return suite
