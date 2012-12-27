#!/usr/bin/env python

from distutils.core import setup

setup(name='pinscheralfred',
      version='1.0',
      description='Pinscher based Python scripts to be used via Alfred',
      author='William Mayor',
      author_email='mail@williammayor.co.uk',
      url='pinscher.williammayor.co.uk',
      requires=['pinschercore'],
      py_modules=['pinscheralfred'],
      )
