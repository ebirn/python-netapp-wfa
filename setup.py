#!/usr/bin/env python

# set env variable DISTUTILS_DEBUG to any value for distutils debugging output

from distutils.core import setup

setup(name='netapp-wfa',
      version='0.0.1',
      description='NetApp OnCommand Workflow Automation REST client',
      author='Erich Birngruber',
      author_email='ebirn@outdated.at',
      license='MIT',
      url='https://www.github.com/ebirn/python-netapp-wfa',
#      scripts=['bin/wfa.py'],
      packages=['netapp' ],
      install_requires=['requests>=2.12.1,<2.13.0']
      )
