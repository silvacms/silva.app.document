# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface


silvaconf.extension_name("silva.app.document")
silvaconf.extension_title("Silva new Document")
silvaconf.extension_depends(["Silva", "silva.core.editor"])


class IExtension(Interface):
    """Silva new style Document Extension.
    """


install = DefaultInstaller("silva.app.document", IExtension)

