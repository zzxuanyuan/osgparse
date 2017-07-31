# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Zhe Zhang, zzxuanyuan@gmail.com
#
# This module is part of failure analysis of OSG project and is released under
# the BSD License: https://opensource.org/licenses/BSD-3-Clause

from osgparse import cli

__version__ = '0.1.0'

def format(ifile, ofile):
	preJobSet = set()
	curJobSet = set()
	preJobLifeCycleDict = {}
	curJobLifeCycleDict = {}
	preSnapShot = Parser.SnapShot("", {})
	curSnapShot = Parser.SnapShot("", {})

	print "1. Job Freq Hisotry Dict:", len(JobLifeCycle.jobFreqHistoryDict.keys())
	print "1. Job Time Hisotry Dict:", len(JobLifeCycle.jobTimeHistoryDict.keys())

	totalLineCount = 0

	with open(ifile, "r") as lines:
		for fname in lines:
			tup = JobLifeCycle.generateLifeCycleFromFile(
				fname, totalLineCount, preJobSet, curJobSet,
				preJobLifeCycleDict, curJobLifeCycleDict, 
				preSnapShot, curSnapShot)
			totalLineCount += tup[0]
			preJobSet = tup[1]
			curJobSet = tup[2]
			preJobLifeCycleDict = tup[3]
			curJobLifeCycleDict = tup[4]
			preSnapShot = tup[5]
			curSnapShot = tup[6]

