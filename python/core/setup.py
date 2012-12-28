from setuptools import setup

setup(
    name='pinscher-core',
    version='0.1.2dev',
    author='William Mayor',
    author_email='mail@williammayor.co.uk',
    url='http://pinscher.williammayor.co.uk',
    license='LICENSE.txt',
    description='Core utilities for interacting with pinscher password files',
    long_description=open('README.txt').read(),
    install_requires=['pycrypto', ],
    packages=['pinschercore', 'pinschercore.test', ],
    test_suite='pinschercore.test',
    scripts=['scripts/pinschercli', 'scripts/pinscheralfred']
)
