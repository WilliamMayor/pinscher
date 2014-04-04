========
pinscher
========

pinscher is a collection of software that manages password collections. pinscher helps you store and retrieve passwords for as many accounts as you like. It can also create random (complex) passwords for you so you can easily have a different password for each account you own.

Your username and password details are stored in strongly encrypted files so you don't have to worry about them being stolen. These encrypted files can be kept on cloud services like Dropbox_ or `Google Drive`_. This way you can share passwords across all of your computers and devices.

.. _Dropbox: https://www.dropbox.com/
.. _Google Drive: https://drive.google.com/

What's in this download?
------------------------

Here you'll find the set of Python functions that can interact with pinscher password files. Using functions in the pinscher module you can insert, update, delete and list passwords, usernames and domains. The module is not intended for end-users, it's intended for developers who wish to include pinscher password storage in their Python software. User-friendly scripts can be found in the scripts directory (and are installed to the path during installation).

Getting pinscher
----------------

The easiest way is to use pip:

    $ pip install pinscher

I would recommend getting virtualenv_ as well. It makes for really easy environment and dependency management.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

Without pip
...........

You can use easy_install instead of pip:

    $ easy_install pinscher

This will grab the source from PyPI and install it for you, it won't sort out the dependencies though. See below for which dependencies you'll need.

*or*

You can get the source code from the `GitHub repo`_ or download it straight from PyPI_. When you have the code you'll need to install everything:

    $ python setup.py install

.. _GitHub repo: https://github.com/WilliamMayor/pinscher
.. _PyPI: http://pypi.python.org/pypi/pinscher

Dependencies
````````````

pinscher relies on PyCrypto_. If you use pip to install the module then you don't need to worry about installing this. If you use one of the other methods then you'll need to follow the installation instructions on the PyCrypto page to go about getting yourself a copy.

.. _PyCrypto: http://pypi.python.org/pypi/pycrypto/2.6
