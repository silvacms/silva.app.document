# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.Version import CatalogedVersion
from Products.Silva.VersionedContent import CatalogedVersionedContent
from zExceptions import BadRequest

from five import grok
from infrae import rest
from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.core.editor.interfaces import ICKEditorResources
from silva.core.editor.transform import render
from silva.core.editor.transform.interfaces import IInputEditorFilter, IDisplayFilter
from silva.core.editor.text import Text
from silva.core.smi import interfaces
from silva.core.smi import smi as silvasmi
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zope.interface import alsoProvides


# Version class for the content
class DocumentVersion(CatalogedVersion):
    """Version of a document object.
    """
    meta_type = 'Silva new Document Version'
    grok.implements(IDocumentVersion)

    def __init__(self, *args):
        super(DocumentVersion, self).__init__(*args)
        self.body = Text(u'<p></p>')

    def fulltext(self):
        return [self.get_title(), unicode(self.body)]


# Content class
class Document(CatalogedVersionedContent):
    """A new style Document.
    """
    meta_type = 'Silva new Document'

    grok.implements(IDocument)
    silvaconf.version_class(DocumentVersion)
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
        if self.content:
            return unicode(render(
                'body', self.content, self.request, IDisplayFilter))
        return _('This content is not available.')


class DocumentEditPage(silvasmi.SMIPage):
    """CKEditor edit page for silva document.
    """
    grok.context(IDocument)
    grok.implements(interfaces.IEditTab,
                    interfaces.ISMITabIndex,
                    interfaces.ISMINavigationOff)
    grok.name('tab_edit')
    tab = 'edit'

    def update(self):
        alsoProvides(self.request, ICKEditorResources)
        self.document = '<p></p>'
        version = self.context.get_editable()
        if version is not None:
            self.document = render(
                'body', version, self.request, IInputEditorFilter)


class RESTSaveDocument(rest.REST):
    """Save document.
    """
    grok.context(IDocument)
    grok.name('silva.app.document.save')

    def POST(self, content):
        version = self.context.get_editable()
        if version is None:
            raise BadRequest('Document is not editable')
        version.body = content





