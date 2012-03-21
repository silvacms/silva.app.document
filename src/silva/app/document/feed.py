# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaMetadata.interfaces import IMetadataService
from five import grok
from zope.component import getUtility, getMultiAdapter
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import IFeedEntry, IVersionManager

from .interfaces import IDocumentContent, IDocumentDetails

class DocumentFeedEntry(grok.MultiAdapter):
    grok.adapts(IDocumentContent)
    grok.provides(IFeedEntry)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.version = self.context.get_viewable()
        self.manager = IVersionManager(self.version)
        self.get_metadata = getUtility(IMetadataService).getMetadataValue

    def id(self):
        return self.url()

    def title(self):
        return self.get_metadata(self.version, 'silva-content', 'maintitle')

    def html_description(self):
        if self.version is not None:
            details = getMultiAdapter(
                (self.version, self.request), IDocumentDetails)
            return details.get_introduction(length=256)
        return u''

    def description(self):
        return self.get_metadata(
            self.version, 'silva-extra', 'content_description')

    def url(self):
        return absoluteURL(self.context, self.request)

    def authors(self):
        author = self.get_metadata(self.version, 'silva-extra', 'lastauthor')
        return [author]

    def date_updated(self):
        return self.get_metadata(
            self.version, 'silva-extra', 'modificationtime')

    def date_published(self):
        return self.manager.get_publication_date()

    def subject(self):
        return self.get_metadata(self.version, 'silva-extra', 'subject')

    def keywords(self):
        keywords = self.get_metadata(self.version, 'silva-extra', 'keywords')
        return [keywords]

