
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


