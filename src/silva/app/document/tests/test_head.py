# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.views.tests.test_head import HEADTestCase, PUBLIC_HEADERS_EXPECTED, AUTH, PRIVATE_HEADERS_EXPECTED


class DocumentHEADTestCase(HEADTestCase):

    def test_document(self):
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Document')
        self.check_headers(
            '/root/document', {}, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_document_auth(self):
        factory = self.root.manage_addProduct['silva.app.document']
        factory.manage_addDocument('document', 'Document')
        self.check_headers(
            '/root/document', AUTH, PUBLIC_HEADERS_EXPECTED)
        self.assertEquals(
            "", self.response.getBody(), "response should be empty")
        self.assertEmptyResponse()

    def test_document_auth_private(self):
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        self.set_private(self.root.document)
        self.check_headers(
            '/root/document', AUTH, PRIVATE_HEADERS_EXPECTED)
        self.assertEmptyResponse()



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentHEADTestCase))
    return suite
