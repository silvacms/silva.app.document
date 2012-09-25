# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import lxml
import cgi

from five import grok
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.base import TransformationFilter
from silva.app.document.interfaces import IDocumentContentVersion
from zope.publisher.interfaces.browser import IBrowserRequest


class InsertTitle(TransformationFilter):
    """When editing, we insert the title as the first node in the tree.
    """
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(100)
    grok.adapts(IDocumentContentVersion, IBrowserRequest)

    def __call__(self, tree):
        title = self.context.get_title().strip()
        if title:
            tree.insert(0, lxml.html.fragment_fromstring(
                    cgi.escape(title), create_parent='h1'))


class SaveTitle(TransformationFilter):
    """On saving from the editor, look for the first h1 or h2 to set as
    document title.
    """
    grok.implements(ISaveEditorFilter)
    grok.provides(ISaveEditorFilter)
    grok.order(100)
    grok.adapts(IDocumentContentVersion, IBrowserRequest)

    def __call__(self, tree):
        nodes = tree.xpath('//h1[1]')
        if len(nodes):
            node = nodes[0]
            title = node.xpath('normalize-space(.)')
            node.getparent().remove(node)
        else:
            title = u''
        self.context.set_title(title)
