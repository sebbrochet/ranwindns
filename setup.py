#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from ranwindns import __version__, __author__
from distutils.core import setup

setup(name='ranwindns',
      version=__version__,
      description='Windows DNS Server changes tracker',
      long_description='This command-line tool lets you track record changes made on a Windows DNS Server between successive runs. You get a mail for each server change with the details of the change.',
      author=__author__,
      author_email='contact@sebbrochet.com',
      url='https://code.google.com/p/ranwindns/',
      platforms=['win32'],
      license='MIT License',
      install_requires=['pywin32, WMI'],
      package_dir={ 'ranwindns': 'lib/ranwindns' },
      packages=[
         'ranwindns',
      ],
      scripts=[
         'bin/ranwindns.py',
         'bin/list_windns.py'
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Win32 (MS Windows)',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Topic :: System :: Monitoring',
          ],
      )