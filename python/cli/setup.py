#!/usr/bin/env python

from distutils.core import setup

setup(name='pinscher-cli',
      version='1.0',
      description='Terminal interface for Pinscher password files',
      author='William Mayor',
      author_email='mail@williammayor.co.uk',
      url='pinscher.williammayor.co.uk',
      requires=['pinschercore'],
      py_modules=['pinschercli'],
      )
