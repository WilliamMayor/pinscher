from setuptools import setup

setup(
    name='pinscher-core',
    version='0.1.2dev',
    author='William Mayor',
    author_email='mail@williammayor.co.uk',
    packages=['pinschercore', 'pinschercore.test', ],
    url='http://pinscher.williammayor.co.uk',
    license='LICENSE.txt',
    description='Core utilities for interacting with pinscher password files',
    long_description=open('README.txt').read(),
    install_requires=['pycrypto', ],
)
