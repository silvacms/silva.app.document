# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import lxml.html

from Products.Silva.Version import Version
from Products.Silva.VersionedContent import VersionedContent
from AccessControl.security import checkPermission

from five import grok
from zope.component import getMultiAdapter, getUtility
from zope.publisher.browser import BrowserView
from zope.traversing.browser import absoluteURL
from zope.publisher.browser import TestRequest

from silva.core import conf as silvaconf
from silva.core.smi.content import IEditScreen
from silva.core.conf.interfaces import ITitledContent
from silva.core.editor.interfaces import ITextIndexEntries
from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import IDisplayFilter
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.interfaces.adapters import IIndexEntries
from silva.core.references.interfaces import IReferenceService
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IContentURL
from silva.ui.rest.base import Screen, PageREST
from silva.ui.rest.container import ListingPreview
from zeam.form import silva as silvaforms

from .interfaces import IDocumentContent, IDocumentContentVersion
from .interfaces import IDocument, IDocumentVersion
from .interfaces import IDocumentDetails


class DocumentContentVersion(Version):
    """Version of a document object.
    """
    grok.baseclass()
    grok.implements(IDocumentContentVersion)

    def __init__(self, *args):
        super(DocumentContentVersion, self).__init__(*args)
        self.body = Text("body", u'<p></p>')

    def fulltext(self):
        fulltext = self.body.fulltext(self, TestRequest())
        fulltext.append(self.get_title())
        return fulltext


# Version class for the content
class DocumentVersion(DocumentContentVersion):
    """Version of a document object.
    """
    grok.implements(IDocumentVersion)
    meta_type = 'Silva Document Version'


class DocumentContent(VersionedContent):
    """A new style Document.
    """
    grok.baseclass()
    grok.implements(IDocumentContent)
    silvaconf.version_class(DocumentContentVersion)


# Content class
class Document(DocumentContent):
    """A new style Document.
    """
    grok.implements(IDocument)
    meta_type = 'Silva Document'

    silvaconf.version_class(DocumentVersion)
    silvaconf.priority(-6)
    silvaconf.icon('document.png')


# Add form
class DocumentAddForm(silvaforms.SMIAddForm):
    """ Add form for Documents
    """
    grok.context(IDocument)
    grok.name('Silva Document')

    fields = silvaforms.Fields(ITitledContent)


# Edit view
class DocumentEdit(PageREST):
    grok.adapts(Screen, IDocumentContent)
    grok.name('content')
    grok.implements(IEditScreen)
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        if checkPermission('silva.ChangeSilvaContent', self.context):
            version = self.context.get_editable()
            if version is not None:
                text = version.body.render(
                    version, self.request, IInputEditorFilter)

                return {"ifaces": ["editor"],
                        "name": "body",
                        "text": text,
                        "configuration": self.context.meta_type}

        url = getMultiAdapter(
            (self.context, self.request),
            IContentURL).preview()
        return {"ifaces": ["preview"],
                "html_url": url}


# Public view
class DocumentPublicView(silvaviews.View):
    """ Public view for Document
    """
    grok.context(IDocumentContent)

    def update(self):
        self.text = None
        if self.content is not None:
            self.text = self.content.body.render(
                self.content, self.request, IDisplayFilter)


class DocumentDetails(BrowserView):
    """Give access to part of the document, like a thumbnail or an
    introduction for it.
    """
    grok.implements(IDocumentDetails)
    DEFAULT_FORMAT = u"""<img src="%s?thumbnail" class="thumbnail" />"""

    def get_thumbnail(self, format=DEFAULT_FORMAT):
        tree = lxml.html.fromstring(unicode(self.context.body))
        results = tree.xpath("//img[@reference][1]")
        if results:
            image = results[0]
            reference_service = getUtility(IReferenceService)
            reference = reference_service.get_reference(
                self.context, name=image.attrib['reference'])
            image_content = reference.target
            return format % absoluteURL(image_content, self.request)
        return None

    def get_introduction(self, length=128):
        return self.context.body.introduction(
            self.context, self.request, max_length=length)

    def get_text(self):
        return self.context.body.render(self.context, self.request)


class DocumentListingPreview(ListingPreview):
    grok.context(IDocumentContent)

    def preview(self):
        previewable = self.context.get_previewable()
        details = getMultiAdapter((previewable, self.request), IDocumentDetails)
        return details.get_introduction()


#Indexes
class DocumentIndexEntries(grok.Adapter):
    grok.implements(IIndexEntries)
    grok.context(IDocumentContent)

    def get_title(self):
        return self.context.get_title()

    def get_entries(self):
        version = self.context.get_viewable()
        if version is None:
            return []
        return ITextIndexEntries(version.body).entries

