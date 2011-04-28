import unittest
from zope.component import getUtility
from Products.Silva.tests.helpers import open_test_file
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import get_content_id
from silva.app.document.testing import FunctionalLayer
from Products.Silva.silvaxml.xmlexport import exportToString


class TestExport(unittest.TestCase):
    layer = FunctionalLayer
    html = """
<div>
  <h1>
    Example</h1>
  <p>
    here is a paragraph...</p>
  <p>
    then comes a <a class="link" target="_self"
    reference="93094ba8-70bd-11e0-b805-c42c0338b1a2">link</a></p>
  <p>
    then comes an image :</p>
  <div class="image default">
    <img alt="location.png"
    reference="a5c84b4a-70bd-11e0-8c0a-c42c0338b1a2">
    <span class="image-caption">location.png</span></div>
</div>
"""

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('example', 'Example')
        self.content = self.root.example
        self.version = self.content.get_editable()
        self.version.body.save_raw_text = self.html

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
        print exportToString(self.root)[0]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestExport))
    return suite
