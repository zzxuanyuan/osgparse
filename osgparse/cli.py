#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Zhe Zhang, zzxuanyuan@gmail.com
#
# This module is part of failure analysis of OSG project and is released under
# the BSD License: https://opensource.org/licenses/BSD-3-Clause

import argparse
import sys

import osgparse

def create_parser():
	print "in create_parse"
	parser = argparse.ArgumentParser(
		prog='osgformat',
		description='Format snapshot FILE(s) to job FILE',
		usage='%(prog)s [OPTIONS] FILE, ...',
	)

	parser.add_argument('filename', help='list of snapshot files that is used to generate job instances')
	parser.add_argument('-i', '--infile', help='the snapshot file as the input')
	parser.add_argument('-o', '--outfile', help='the job instances as the output')
	parser.add_argument('-v', '--version', action='version',version=osgparse.__version__)

	return parser

def main(args=None):
	print "in mian"
	parser = create_parser()
	args = parser.parse_args(args)
	
	if args.outfile:
		stream = open(args.outfile, 'w')
	else:
		stream = sys.stdout

	opts = vars(args)
	print opts
	osgparse.format(**opts)	
	return 0
