
from zope.publisher.interfaces.browser import IBrowserView
from silva.core import interfaces
from zope import  schema


class IDocument(interfaces.IVersionedContent):
    """A new style Document
    """


class IDocumentVersion(interfaces.IVersion):
    """A new style Document version.
    """
    body = schema.Text(
        title=u"Content",
        description=u"HTML content of the document.",
        required=True)



class IDocumentDetails(IBrowserView):
    """Give access to document details.
    """

    def get_thumbnail(format):
        """Return a piece of HTML with the thumbnail of the first
        document image.
        """

    def get_introduction(length=128):
        """Return a piece of HTML with part of the first paragraph.
        """
