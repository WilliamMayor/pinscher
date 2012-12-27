#!/usr/bin/env python

from distutils.core import setup

setup(name='pinschercore',
      version='1.0',
      description='Core utilities for dealing with Pinscher password files',
      author='William Mayor',
      author_email='mail@williammayor.co.uk',
      url='pinscher.williammayor.co.uk',
      requires=['pycrypto'],
      py_modules=['pinschercore'],
      )
