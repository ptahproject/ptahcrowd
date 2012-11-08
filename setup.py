import os
from setuptools import setup, find_packages

version = '0.2'

install_requires = ['setuptools',
                    'ptah >= 0.8.0',
                    "requests >= 0.6.6",
                    ]
tests_require = install_requires + ['nose']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


setup(name='ptahcrowd',
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
      url='https://github.com/ptahproject/ptahcrowd/',
      license='BSD-derived',
      packages=find_packages(),
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='nose.collector',
      include_package_data=True,
      zip_safe=False,
      message_extractors={'ptahcrowd': [
        ('static/**', 'ignore', None),
        ('tests/**.py', 'ignore', None),
        ('**.py', 'python', None),
        ('**.pt', 'lingua_xml', None),
      ]},
      )
