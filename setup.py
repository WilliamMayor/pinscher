from setuptools import setup

setup(
    name='pinscher',
    version='0.2dev',
    author='William Mayor',
    author_email='mail@williammayor.co.uk',
    url='http://pinscher.williammayor.co.uk',
    license='LICENSE.txt',
    description='Core utilities for interacting with pinscher password files',
    long_description=open('README.md').read(),
    install_requires=[],
    packages=['pinscher', ],
    entry_points={
        'console_scripts': [
            'pinscher = pinscher.scripts.pinscher:script_entry_point'
        ],
        'gui_scripts': []
    }
)
