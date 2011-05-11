from Products.Silva.silvaxml import xmlimport
from silva.core.editor.transform.silvaxml import NS_URI as NS_EDITOR_URI
from silva.core.editor.transform.silvaxml.xmlimport import TextHandler
from silva.app.document.silvaxml import NS_URI
from silva.core import conf as silvaconf

silvaconf.namespace(NS_URI)


class DocumentHandler(xmlimport.SilvaBaseHandler):
    silvaconf.name('document')

    def getOverrides(self):
        return {(xmlimport.NS_URI, 'content'): DocumentVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'document'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            factory = self.parent().manage_addProduct['silva.app.document']
            factory.manage_addDocument(uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'document'):
            self.notifyImport()


class DocumentVersionHandler(xmlimport.SilvaBaseHandler):

    def getOverrides(self):
        return {(NS_URI, 'body'): DocumentVersionBodyHandler}

    def startElementNS(self, name, qname, attrs):
        if (xmlimport.NS_URI, 'content') == name:
            uid = attrs[(None, 'version_id')].encode('utf-8')
            factory = self.parent().manage_addProduct['silva.app.document']
            factory.manage_addDocumentVersion(uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if (xmlimport.NS_URI, 'content') == name:
            xmlimport.updateVersionCount(self)
            self.storeMetadata()
            self.storeWorkflow()


class DocumentVersionBodyHandler(xmlimport.SilvaBaseHandler):

    def getOverrides(self):
        return {(NS_EDITOR_URI, 'text'): TextHandler}

    def startElementNS(self, name, qname, attrs):
        if (NS_URI, 'body') == name:
            self.setResult(self.parent().body)

    def endElementNS(self, name, qname):
        pass


