import os
import sys
import logging
import multiprocessing  # atexit exception
from setuptools import setup, find_packages

version = '0.2dev'

install_requires = ['setuptools',
                    'ptah >= 0.3.1',
                    "requests >= 0.6.6",
                    ]
PY2 = sys.version_info[0] == 2
if PY2:
    # Temporarily switching off oauth2 for Python 3.2.
    # This impacts the twitter and linkedin providers.
    install_requires.append("oauth2 >= 1.1.3")

tests_require = install_requires + ['nose']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


setup(name='ptah_crowd',
      version=version,
      description=('User management for Ptah.'),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: Implementation :: CPython",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Ptah Project',
      author_email='ptahproject@googlegroups.com',
      url='https://github.com/ptahproject/ptah_crowd/',
      license='BSD-derived',
      packages=find_packages(),
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='nose.collector',
      include_package_data=True,
      zip_safe=False,
      message_extractors={'ptah_crowd': [
        ('static/**', 'ignore', None),
        ('tests/**.py', 'ignore', None),
        ('**.py', 'python', None),
        ('**.pt', 'lingua_xml', None),
      ]},
      )
