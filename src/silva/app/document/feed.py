from five import grok
from zope.component import getUtility

from silva.core.interfaces import IFeedEntry, IVersionManager
from Products.SilvaMetadata.interfaces import IMetadataService
from zope.traversing.browser import absoluteURL
from silva.app.document import interfaces


class DocumentFeedEntry(grok.MultiAdapter):
    grok.adapts(interfaces.IDocument)
    grok.provides(IFeedEntry)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.version = self.context.get_viewable()
        self.manager = IVersionManager(self.version)
        self.metadata = getUtility(IMetadataService).getMetadata(self.version)

    def id(self):
        return self.url()

    def title(self):
        return self.context.get_title()

    def html_description(self):
        if self.version is not None:
            return self.version.body.render_intro(self.version, self.request)
        return u''

    def description(self):
        return u''

    def url(self):
        return absoluteURL(self.context, self.request)

    def authors(self):
        return []

    def date_updated(self):
        return self.metadata.get('silva-extra', 'modificationtime')

    def date_published(self):
        return self.manager.get_publication_date()

    def subject(self):
        return u''

    def keywords(self):
        return self.version.fulltext()


