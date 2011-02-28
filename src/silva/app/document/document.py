# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.Version import CatalogedVersion
from Products.Silva.VersionedContent import CatalogedVersionedContent

from five import grok
from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.core.editor.interfaces import ICKEditorViewResources, ITextIndexEntries
from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import IInputEditorFilter, IDisplayFilter
from silva.core.interfaces.adapters import IIndexEntries
from silva.core.smi import interfaces
from silva.core.smi import smi as silvasmi
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.lifecycleevent.interfaces import IObjectCreatedEvent


# Version class for the content
class DocumentVersion(CatalogedVersion):
    """Version of a document object.
    """
    meta_type = 'Silva new Document Version'
    grok.implements(IDocumentVersion)

    def __init__(self, *args):
        super(DocumentVersion, self).__init__(*args)
        self.body = Text("body", u'<p></p>')

    def fulltext(self):
        return [self.get_title(), unicode(self.body)]


# Content class
class Document(CatalogedVersionedContent):
    """A new style Document.
    """
    meta_type = 'Silva new Document'

    grok.implements(IDocument)
    silvaconf.version_class(DocumentVersion)
    silvaconf.priority(-6)
    silvaconf.icon('document.png')


# Add form
class DocumentAddForm(silvaforms.SMIAddForm):
    """ Add form for Documents
    """
    silvaconf.context(IDocument)
    silvaconf.name('Silva new Document')

    fields = silvaforms.Fields(ITitledContent)


# Public view
class DocumentPublicView(silvaviews.View):
    """ Public view for Document
    """
    silvaconf.context(IDocument)

    def render(self):
        if self.content is not None:
            return self.content.body.render(self.content, self.request, IDisplayFilter)
        return _('This content is not available.')


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
    version = content.get_editable()
    version.body.save_raw_text(u'<h1>' + version.get_title() + u'</h1>')
