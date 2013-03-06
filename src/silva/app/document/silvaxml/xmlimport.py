# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.app.document.silvaxml import NS_DOCUMENT_URI
from silva.core import conf as silvaconf
from silva.core.editor.transform.silvaxml import NS_EDITOR_URI
from silva.core.editor.transform.silvaxml.xmlimport import TextHandler
from silva.core.xml import handlers, NS_SILVA_URI

silvaconf.namespace(NS_DOCUMENT_URI)


class DocumentHandler(handlers.SilvaHandler):
    silvaconf.name('document')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): DocumentVersionHandler}

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.document']
        factory.manage_addDocument(identifier, '', no_default_version=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_DOCUMENT_URI, 'document'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_DOCUMENT_URI, 'document'):
            self.notifyImport()


class DocumentVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {(NS_DOCUMENT_URI, 'body'): DocumentVersionBodyHandler}

    def _createVersion(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.document']
        factory.manage_addDocumentVersion(identifier, '')

    def startElementNS(self, name, qname, attrs):
        if (NS_SILVA_URI, 'content') == name:
            self.createVersion(attrs)

    def endElementNS(self, name, qname):
        if (NS_SILVA_URI, 'content') == name:
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class DocumentVersionBodyHandler(handlers.SilvaHandler):

    def getOverrides(self):
        return {(NS_EDITOR_URI, 'text'): TextHandler}

    def startElementNS(self, name, qname, attrs):
        if (NS_DOCUMENT_URI, 'body') == name:
            self.setResult(self.parent().body)

    def endElementNS(self, name, qname):
        pass


