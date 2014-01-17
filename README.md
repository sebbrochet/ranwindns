ranwindns
=========

Track changes on your Windows Server DNS

Requirements:
-------------

* Windows box and a Windows DNS server
* Python 2.6 or higher
* Create/Commit rights to a CVS or Subversion repository
* cvs or svn binaries in the PATH

Installation:
-------------

To install, just do:

python setup.py install

Usage:
------

usage: ranwindns.py [-h] [-c CONFIG] [--v] action

Windows DNS Server changes tracker.

positional arguments:
  action                Action to execute (GENCONFIG or RUN)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file to use or create
  --v                   Print program version and exit.

GENCONFIG: generate default configuration file, to be customized with your environment.
RUN: get configuration for each server and generates corresponding files.

Documentation:
--------------

Please visit the project page at: https://code.google.com/p/ranwindns/
