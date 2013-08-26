# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '3.0.1'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.app.document',
      version=version,
      description="Document content for Silva 3.x with WYSIWYG Editor.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='document silva wysiwyg',
      author='Antonin Amand',
      author_email='info@infrae.com',
      url='',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'Products.Silva',
        'Products.SilvaExternalSources',
        'five.grok',
        'lxml',
        'setuptools',
        'silva.core.conf',
        'silva.core.editor',
        'silva.core.interfaces',
        'silva.core.references',
        'silva.core.smi',
        'silva.core.views',
        'silva.core.xml',
        'silva.core.services',
        'silva.translations',
        'silva.ui',
        'zeam.form.silva',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
      ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
