#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Andi Albrecht, albrecht.andi@gmail.com
#
# This module is part of python-sqlparse and is released under
# the BSD License: https://opensource.org/licenses/BSD-3-Clause

import argparse
import sys

import osgparse

def create_parser():
	parser = argparse.ArgumentParser(
		prog='osgformat',
		description='Format snapshot FILE(s) to job FILE',
#		useage='%(prog) [OPTIONS] FILE, ...',
	)

	parser.add_argument('-f', '--filename', help='the file that contains all snapshot files')
	parser.add_argument('-i', '--input', help='the snapshot file as the input')
	parser.add_argument('-o', '--output', help='the job instances as the output')
	parser.add_argument('-v', '--version', action='version',version=osgparse.__version__)

	return parser

def main(args=None):
	parser = create_parser()
	args = parser.parse_args(args)
	return 0
