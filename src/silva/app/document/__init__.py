# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Persistence import Persistent

from five import grok
from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from silva.core.interfaces import IContainerPolicy
from silva.core.editor.interfaces import ICKEditorService
from zope.interface import Interface
from zope.component import queryUtility


silvaconf.extension_name("silva.app.document")
silvaconf.extension_title("Silva new Document")
silvaconf.extension_depends(["Silva", "silva.core.editor"])


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
            root.manage_addProduct['silva.core.editor'].manage_addCKEditorService()
        root.service_containerpolicy.register(
            'Silva new Document', DocumentPolicy, -1)



install = DocumentInstaller("silva.app.document", IExtension)

