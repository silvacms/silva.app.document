# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.testing import SilvaLayer
import silva.app.document
import transaction


class SilvaDocumentLayer(SilvaLayer):
    default_packages = SilvaLayer.default_packages + [
        'silva.app.document'
        ]

    def _install_application(self, app):
        super(SilvaDocumentLayer, self)._install_application(app)
        app.root.service_extensions.install('silva.app.document')
        transaction.commit()

FunctionalLayer = SilvaDocumentLayer(silva.app.document)
