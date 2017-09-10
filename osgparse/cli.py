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

	parser.add_argument('-f', '--filename', help='list of snapshot files that is used to generate job instances')
	parser.add_argument('-i', '--infile', help='the snapshot file as the input')
	parser.add_argument('-j', '--jobinstances', help='the job instances file as input')
	parser.add_argument('-ts','--timeseries', help='the time series file as input')
	parser.add_argument('-o', '--outfile', help='the job instances as the output or the time series as the output')
	parser.add_argument('-c', '--command', help='the function to process the data')
	parser.add_argument('-pt','--plottype', help='the type of information should be contained in the plot')
	parser.add_argument('-r', '--resource', help='the resource name to plot')
	parser.add_argument('-l', '--label', help='the label name to plot')
	parser.add_argument('-tp', '--timepoint', help='the time point to differentiate survivors and victims')
	parser.add_argument('-ex', '--exclude', help='filter classes that are exclusive')
	parser.add_argument('-in', '--include', help='filter classes that are inclusive')
	parser.add_argument('-rm', '--regressionmodel', help='regression model')
	parser.add_argument('-cm', '--classificationmodel', help='classification model')
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
	if args.command == "format":
		osgparse.format(**opts)
	elif args.command == "timeseries":
		osgparse.timeseries(**opts)
	elif args.command == "plot":
		osgparse.plot(**opts)
	elif args.command == "classify":
		osgparse.classify(**opts)
	elif args.command == "predict":
		osgparse.predict(**opts)
	elif args.command == "changelabel":
		osgparse.changelabel(**opts)
	elif args.command == "filter":
		osgparse.filter(**opts)
	return 0
