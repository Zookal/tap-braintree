#!/usr/bin/env python

from setuptools import setup, find_packages
import os.path


setup(name='tap-braintree',
      version='0.1.1',
      description='Taps BrainTree data',
      author='Stitch',
      url='https://github.com/stitchstreams/tap-braintree',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_braintree'],
      install_requires=[
          'stitchstream-python>=0.5.0',
          'requests==2.12.4',
          'backoff==1.3.2',
          'python-dateutil==2.6.0',
      ],
      entry_points='''
          [console_scripts]
          tap-braintree=tap_braintree:main
      ''',
      packages=['tap_braintree'],
      package_data = {
          'tap_braintree': [
              'transactions.json',
          ],
      }
)