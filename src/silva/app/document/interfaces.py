# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core import interfaces
from Products.SilvaExternalSources.interfaces import ISourceEditableVersion
from zope import  schema
from zope.publisher.interfaces.browser import IBrowserView


class IDocumentContent(interfaces.IVersionedContent):
    """A new style Document

    You should use this as base content if you want to extend the
    document type.
    """


class IDocument(IDocumentContent):
    """A Document
    """


class IDocumentContentVersion(ISourceEditableVersion):
    """A new style Document version

    You should use this as base version if you want to extend the
    document.
    """
    body = schema.Text(
        title=u"Content",
        description=u"HTML content of the document.",
        required=True)


class IDocumentVersion(IDocumentContentVersion):
    """Document version
    """


class IDocumentDetails(IBrowserView):
    """Give access to document details.
    """

    def get_title():
        """Return the document title.
        """

    def get_thumbnail(format):
        """Return a piece of HTML with the thumbnail of the first
        document image.
        """

    def get_thumbnail_url():
        """Return the URL of the thumbnail of the first image in the
        document.
        """

    def get_image_url():
        """Return the URL of the first image in the document.
        """

    def get_introduction(length=128, words=None):
        """Return a piece of HTML with part of the first
        paragraph. You can either control the number of characters or
        words contained inside the introduction.
        """

    def get_text(downgrade_titles=False):
        """Return the full HTML (without the title) of the document.
        """
