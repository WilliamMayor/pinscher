from setuptools import setup

setup(
    name='pinscher-cli',
    version='1.0',
    description='Terminal interface for Pinscher password files',
    author='William Mayor',
    author_email='mail@williammayor.co.uk',
    packages=['pinschercli', 'pinschercli.test', ],
    url='http://pinscher.williammayor.co.uk',
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
    install_requires=['pinscher-core', ],
)
