from setuptools import setup

setup(
    name='pinscher',
    version='0.3dev',
    author='William Mayor',
    author_email='mail@williammayor.co.uk',
    url='http://pinscher.williammayor.co.uk',
    license='LICENSE.txt',
    description='Core utilities for interacting with pinscher password files',
    long_description=open('README.txt').read(),
    install_requires=['docopt==0.6.1',
                      'nose==1.3.0',
                      'pycrypto==2.6.1'],
    packages=['pinscher', ],
    scripts=['bin/pin']
)
