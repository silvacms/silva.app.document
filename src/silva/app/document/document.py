# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import lxml.html

from Products.Silva.Version import Version
from Products.Silva.VersionedContent import VersionedContent

from five import grok
from zope.component import getMultiAdapter, getUtility
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.publisher.browser import BrowserView
from zope.traversing.browser import absoluteURL

from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.app.document.interfaces import IDocumentDetails
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
from silva.core.views.interfaces import ISilvaURL
from silva.translations import translate as _
from silva.ui.rest.base import Screen, PageREST
from zeam.form import silva as silvaforms



# Version class for the content
class DocumentVersion(Version):
    """Version of a document object.
    """
    meta_type = 'Silva Document Version'
    grok.implements(IDocumentVersion)

    def __init__(self, *args):
        super(DocumentVersion, self).__init__(*args)
        self.body = Text("body", u'<p></p>')

    def fulltext(self):
        return [self.get_title(), unicode(self.body)]


# Content class
class Document(VersionedContent):
    """A new style Document.
    """
    meta_type = 'Silva Document'

    grok.implements(IDocument)
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
    grok.adapts(Screen, IDocument)
    grok.name('content')
    grok.implements(IEditScreen)
    grok.require('silva.ChangeSilvaContent')

    def payload(self):
        version = self.context.get_editable()
        if version is not None:
            text = version.body.render(
                version, self.request, IInputEditorFilter)

            return {"ifaces": ["editor"],
                    "name": "body",
                    "text": text}

        url = getMultiAdapter((self.context, self.request), ISilvaURL).preview()
        return {"ifaces": ["preview"],
                "html_url": url}


# Public view
class DocumentPublicView(silvaviews.View):
    """ Public view for Document
    """
    grok.context(IDocument)

    def render(self):
        if self.content is not None:
            return self.content.body.render(
                self.content, self.request, IDisplayFilter)
        return _('This content is not available.')


class DocumentDetails(BrowserView):
    """Give access to part of the document, like a thumbnail or an
    introduction for it.
    """
    grok.implements(IDocumentDetails)
    DEFAULT_FORMAT = u"""<img src="%s?thumbnail" class="thumbnail" />"""

    # XXX this code may be moved to some adapter, so it can be used
    # to get the thumbnail object without a request
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
        parts = self.context.body.render_intro(
            self.context, self.request, max_length=128)
        if parts:
            return parts[0]
        return u''


#Indexes
class DocumentIndexEntries(grok.Adapter):
    grok.implements(IIndexEntries)

    def get_title(self):
        return self.context.get_title()

    def get_entries(self):
        version = self.context.get_viewable()
        if version is None:
            return []
        return map(
            lambda e: (e.anchor, e.title),
            ITextIndexEntries(version.body).entries)


@grok.subscribe(IDocument, IObjectCreatedEvent)
def set_title_of_new_document(content, event):
    """If a document is added, it will contain by default its title.
    """
    if IObjectCopiedEvent.providedBy(event):
        # Don't override a copied document !
        return
    version = content.get_editable()
    if version is not None:
        version.body.save_raw_text(u'<h1>' + version.get_title() + u'</h1>')


