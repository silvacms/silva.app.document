from five import grok
from zope.interface import Interface
from silva.app.document import interfaces
from Products.Silva.silvaxml import xmlexport
from silva.core.editor.transform.silvaxml.export import TextProducerProxy
from silva.app.document.silvaxml import NS_URI

xmlexport.theXMLExporter.registerNamespace('silvaappdoc', NS_URI)


class DocumentProducer(xmlexport.VersionedContentProducer):
    grok.adapts(interfaces.IDocument, Interface)

    def sax(self):
        self.startElementNS(NS_URI, 'document', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(NS_URI, 'document')


class DocumentVersionProducer(xmlexport.SilvaBaseProducer):
    grok.adapts(interfaces.IDocumentVersion, Interface)

    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.metadata()
        self.startElementNS(NS_URI, 'body')
        proxy = TextProducerProxy(self.context, self.context.body)
        proxy.sax(self)
        self.endElementNS(NS_URI, 'body')
        self.endElement('content')


