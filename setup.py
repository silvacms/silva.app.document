from setuptools import setup, find_packages
import os

version = '1.0dev'

setup(name='silva.app.document',
      version=version,
      description="Document content for Silva 2.x with WYSIWYG Editor.",
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
        'five.grok',
        'setuptools',
        'silva.core.conf',
        'silva.core.editor',
        'silva.core.interfaces',
        'silva.core.references',
        'silva.core.views',
        'silva.translations',
        'silva.ui',
        'zope.component',
        'zope.interface',
      ],
      )
