# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface
from silva.app.document import interfaces
from Products.Silva.silvaxml import xmlexport
from silva.core.editor.transform.silvaxml.xmlexport import TextProducerProxy
from silva.app.document.silvaxml import NS_DOCUMENT_URI


xmlexport.theXMLExporter.registerNamespace(
    'silva-app-document', NS_DOCUMENT_URI)


class DocumentProducer(xmlexport.VersionedContentProducer):
    grok.adapts(interfaces.IDocument, Interface)

    def sax(self):
        self.startElementNS(
            NS_DOCUMENT_URI, 'document', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(
            NS_DOCUMENT_URI, 'document')


class DocumentVersionProducer(xmlexport.SilvaBaseProducer):
    grok.adapts(interfaces.IDocumentVersion, Interface)

    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.metadata()
        self.startElementNS(
            NS_DOCUMENT_URI, 'body')
        TextProducerProxy(self.context, self.context.body).sax(self)
        self.endElementNS(
            NS_DOCUMENT_URI, 'body')
        self.endElement('content')


