# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaMetadata.interfaces import IMetadataService
from five import grok
from silva.app.document.interfaces import IDocument, IDocumentDetails
from silva.core.interfaces import IFeedEntry, IVersionManager
from zope.component import getUtility, getMultiAdapter
from zope.traversing.browser import absoluteURL


class DocumentFeedEntry(grok.MultiAdapter):
    grok.adapts(IDocument)
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
            details = getMultiAdapter(
                (self.version, self.request), IDocumentDetails)
            return details.get_intro()
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


