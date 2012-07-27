# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaMetadata.interfaces import IMetadataService
from five import grok
from zope.component import getUtility, getMultiAdapter
from zope.component import queryMultiAdapter
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import IFeedEntry, IVersionManager

from .interfaces import IDocumentContent, IDocumentContentVersion
from .interfaces import IDocumentDetails


class DocumentFeedEntry(grok.MultiAdapter):
    grok.adapts(IDocumentContentVersion, IHTTPRequest)
    grok.provides(IFeedEntry)
    grok.implements(IFeedEntry)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.get_metadata = getUtility(IMetadataService).getMetadataValue

    def id(self):
        return self.url()

    def title(self):
        return self.get_metadata(self.context, 'silva-content', 'maintitle')

    def html_description(self):
        if self.context is not None:
            details = getMultiAdapter(
                (self.context, self.request), IDocumentDetails)
            return details.get_introduction(length=256)
        return u''

    def description(self):
        return self.get_metadata(
            self.context, 'silva-extra', 'content_description')

    def url(self):
        return absoluteURL(self.context.get_silva_object(), self.request)

    def authors(self):
        return [self.get_metadata(self.context, 'silva-extra', 'lastauthor')]

    def date_updated(self):
        return self.get_metadata(
            self.context, 'silva-extra', 'modificationtime')

    def date_published(self):
        manager = IVersionManager(self.context)
        return manager.get_publication_datetime()

    def subject(self):
        return self.get_metadata(self.context, 'silva-extra', 'subject')

    def keywords(self):
        keywords = self.get_metadata(self.context, 'silva-extra', 'keywords')
        if keywords:
            return [keywords]
        return []


@grok.adapter(IDocumentContent, IHTTPRequest)
@grok.provider(IFeedEntry)
@grok.implementer(IFeedEntry)
def document_feed(document, request):
    viewable = document.get_viewable()
    if viewable is None:
        # This will be intercepted by the ZCA and fail the lookup
        raise ValueError("No viewable version")
    return queryMultiAdapter((viewable, request), IFeedEntry)
