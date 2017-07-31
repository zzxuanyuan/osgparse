#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Zhe Zhang, zzxuanyuan@gmail.com
#
# This module is part of the project of analyzing failure of OSG glidein jobs and is released under
# the BSD License: https://opensource.org/licenses/BSD-3-Clause

"""Entrypoint module for `python -m osgparse`.

Why does this file exist, and why __main__? For more info, read:
- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""

import sys

from osgparse.cli import main

if __name__ == '__main__':
	sys.exit(main())
