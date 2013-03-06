# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.app.document import interfaces
from silva.app.document.silvaxml import NS_DOCUMENT_URI
from silva.core.editor.transform.silvaxml.xmlexport import TextProducerProxy
from silva.core.xml import producers
from zope.interface import Interface


class DocumentProducer(producers.SilvaVersionedContentProducer):
    grok.adapts(interfaces.IDocument, Interface)

    def sax(self):
        self.startElementNS(
            NS_DOCUMENT_URI, 'document', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElementNS(
            NS_DOCUMENT_URI, 'document')


class DocumentVersionProducer(producers.SilvaProducer):
    grok.adapts(interfaces.IDocumentVersion, Interface)

    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.sax_metadata()
        self.startElementNS(
            NS_DOCUMENT_URI, 'body')
        TextProducerProxy(self.context, self.context.body).sax(self)
        self.endElementNS(
            NS_DOCUMENT_URI, 'body')
        self.endElement('content')


