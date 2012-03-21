
from silva.core import interfaces
from zope import  schema
from zope.publisher.interfaces.browser import IBrowserView


class IDocumentContent(interfaces.IVersionedContent):
    """A new style Document.

    You should use this as base content if you want to extend the
    document type.
    """


class IDocument(IDocumentContent):
    """A Document.
    """


class IDocumentContentVersion(interfaces.IVersion):
    """A new style Document version.

    You should use this as base version if you want to extend the
    document.
    """
    body = schema.Text(
        title=u"Content",
        description=u"HTML content of the document.",
        required=True)


class IDocumentVersion(IDocumentContentVersion):
    """Document version.
    """


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
