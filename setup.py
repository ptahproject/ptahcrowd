import sys, os
from setuptools import setup, find_packages

version='0.1'

install_requires = ['setuptools',
                    'ptah',
                    'pyramid_beaker',
                    'repoze.sendmail',
                    ]
tests_require = ['nose']


setup(name='biga',
      version=version,
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Ptah Project',
      author_email='ptahproject@googlegroups.com',
      url='https://github.com/ptahproject/biga/',
      license='BSD-derived',
      packages=find_packages(),
      install_requires = install_requires,
      tests_require = tests_require,
      test_suite = 'nose.collector',
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'ptah': ['package = biga'],
        },
      )
