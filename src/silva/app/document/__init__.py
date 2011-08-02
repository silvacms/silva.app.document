# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Persistence import Persistent

from five import grok
from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from silva.core.editor.interfaces import ICKEditorService
from silva.core.interfaces import IContainerPolicy, IPublicationWorkflow
from silva.core.interfaces.events import IInstalledExtensionEvent
from zope.component import queryUtility
from zope.interface import Interface


silvaconf.extension_name("silva.app.document")
silvaconf.extension_title("Silva Document")
silvaconf.extension_depends(["Silva", "silva.core.editor"])
silvaconf.extension_default()


class DocumentPolicy(Persistent):
    grok.implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        factory = container.manage_addProduct['silva.app.document']
        factory.manage_addDocument('index', title)


class IExtension(Interface):
    """Silva new style Document Extension.
    """


class DocumentInstaller(DefaultInstaller):
    """Install the document extension.
    """

    def install_custom(self, root):
        if queryUtility(ICKEditorService) is None:
            factory = root.manage_addProduct['silva.core.editor']
            factory.manage_addCKEditorService()
        root.service_containerpolicy.register(
            'Silva Document', DocumentPolicy, -1)


@grok.subscribe(DocumentInstaller, IInstalledExtensionEvent)
def add_default_document(extension, event):
    root = event.root
    if root.get_default() is None:
        factory = root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('index', 'Welcome to Silva!')
        document = root.index
        version = document.get_editable()
        version.body.save_raw_text('<div><h1>Welcome to Silva!</h1><p>Welcome to Silva! This is the public view. To actually see something interesting, try adding \'/edit\' to your url (if you\'re not already editing, you can <a href="edit">click this link</a>).</p></div>')
        IPublicationWorkflow(document).publish()


install = DocumentInstaller("silva.app.document", IExtension)

