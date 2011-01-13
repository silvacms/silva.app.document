# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import IOutputEditorFilter
from silva.core.editor.transform.base import Transformer
from silva.app.document.interfaces import IDocumentVersion
from zope.publisher.interfaces.browser import IBrowserRequest


class TitleUpdater(Transformer):
    """On saving from the editor, look for the first h1 or h2 to set as
    document title.
    """
    grok.implements(IOutputEditorFilter)
    grok.provides(IOutputEditorFilter)
    grok.order(100)
    grok.adapts(IDocumentVersion, IBrowserRequest)

    def __call__(self, tree):
        title = tree.xpath('normalize-space(//h1[1])')
        if not title:
            title = tree.xpath('normalize-space(//h2[1])')
        if title:
            self.context.set_title(title)
