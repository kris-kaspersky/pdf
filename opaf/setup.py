#!/usr/bin/env python
#DL

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(name='OPAF',
      version='0.9.2-devel01',
      description='Open PDF Analysis Framework',
      long_description="""
PDF files rely on a complex file structure constructed from a set tokens and 
grammar rules. Also each token can be compressed, encrypted or even obfuscated.

**Open PDF Analysis Framework** (OPAF) will understand, decompress, de-obfuscate
these basic PDF elements and present the resulting soup as a clean XML tree.

From there a set of configurable rules can be used to decide what to keep, 
what to cut out and ultimately if it is safe to open the resulting
PDF projection.""",
      author='Felipe Andres Manzano',
      author_email='felipe.andres.manzano@gmail.com',
      url='http://code.google.com/p/opaf/',
      license='New BSD License',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Natural Language :: English',
          ],
      packages=['opaflib','tests'],
      scripts=['opaf.py'],
      install_requires=['ply', 'lzw', 'lxml'],
      test_suite = "tests",
      )
