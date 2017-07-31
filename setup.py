#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Andi Albrecht, albrecht.andi@gmail.com
#
# This setup script is part of the project that analyze failure in OSG and is released under
# the BSD License: https://opensource.org/licenses/BSD-3-Clause

import re

from setuptools import setup, find_packages


def get_version():
	"""Parse __init__.py for version number instead of importing the file."""
	VERSIONFILE = 'osgparse/__init__.py'
	VSRE = r'^__version__ = [\'"]([^\'"]*)[\'"]'
	with open(VERSIONFILE) as f:
		verstrline = f.read()
	mo = re.search(VSRE, verstrline, re.M)
	if mo:
		return mo.group(1)
	raise RuntimeError('Unable to find version in {fn}'.format(fn=VERSIONFILE))


LONG_DESCRIPTION = """
``osgparse`` is a osg job parser module.
It provides support for parsing snapshots from OSG to glidein jobs.

Visit the `project page <https://github.com/zzxuanyuan/osgparse>`_ for
additional information and documentation.

**Example Usage**
"""

setup(
	name='osgparse',
	version=get_version(),
	author='Zhe Zhang',
	author_email='zzxuanyuan@gmail.com',
	url='https://github.com/zzxuanyuan/osgparse',
	description='OSG glidein job parser',
	long_description=LONG_DESCRIPTION,
	license='BSD',
	classifiers=[
		'Development Status :: 0.1',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Topic :: OSG',
		'Topic :: Software Development',
		],
	packages=find_packages(exclude=('tests',)),
	entry_points={
		'console_scripts': [
			'osgparse = osgparse.__main__:main',
		]
	},
)
