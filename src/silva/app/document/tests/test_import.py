import unittest
import lxml.html
from lxml.cssselect import CSSSelector as css

from zope.component import getUtility
from zope.publisher.browser import TestRequest

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from silva.core.references.interfaces import IReferenceService
from silva.app.document.testing import FunctionalLayer
from Products.SilvaExternalSources.editor.interfaces import ISourceInstances


class DocumentImportTest(SilvaXMLTestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_import_simple_document(self):
        self.import_file(
            'test_import_simple_document.silvaxml',
            globs=globals())

        self.assertTrue(hasattr(self.root, 'adoc'))
        doc = self.root.adoc
        self.assertTrue(doc.get_viewable())
        self.assertFalse(doc.get_editable())
        imported_body = unicode(doc['0'].body)
        self.assertEquals(u"""<div>
            <h1>Welcome to Silva!</h1>
            <p>Welcome to Silva! This is the public view. To actually see something interesting, try adding \'/edit\' to your url (if you\'re not already editing, you can <a href="edit">click this link</a>).</p>
          </div>""", imported_body)

    def test_import_references(self):
        self.import_file('test_import_references.silvaxml', globs=globals())
        import_root = self.root.root
        doc = import_root.example
        self.assertTrue(doc)
        version = doc.get_editable()
        self.assertTrue(version)

        reference_service = getUtility(IReferenceService)
        references = list(reference_service.get_references_from(version))
        refs_by_name = dict(map(
            lambda ref:(ref.tags[0], ref),
            references))

        self.assertEquals(2, len(references))
        self.assertEquals(2, len(refs_by_name))
        broken_ref = refs_by_name['93094ba8-70bd-11e0-b805-c42c0338b1a2']
        image_ref = refs_by_name['a5c84b4a-70bd-11e0-8c0a-c42c0338b1a2']
        self.assertEquals(0, broken_ref.target_id)
        self.assertNotEquals(0, image_ref.target_id)
        self.assertTrue('Silva Image', image_ref.target.meta_type)

    def test_import_code_source(self):
        self.import_file(
            'test_import_code_source.silvaxml',
            globs=globals())
        doc = self.root.example
        version = doc.get_editable()
        self.assertTrue(version)
        sources = ISourceInstances(version.body)
        self.assertEquals(1, len(sources.keys()))
        tree = lxml.html.fragment_fromstring(version.body.render(
            version, TestRequest()))
        es = css("div.external-source")(tree)[0]
        self.assertEquals(css("div.author")(es)[0].text, u'ouam')
        self.assertEquals(css("div.source")(es)[0].text, u'wikipedia')
        self.assertEquals(css("div.citation")(es)[0].text.strip(),
            u'blahblahblah')

# """<div>
#     <p>some paragraph..</p>
#     <div class="external-source default">
#     <div class="citation">
#  blahblahblah
#  <div class="author">ouam</div>
#  <div class="source">wikipedia</div>
# </div></div></div>"""


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentImportTest))
    return suite


