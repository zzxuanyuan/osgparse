# Author: Zhe Zhang <zhan0915@huskers.unl.edu>

# This file contains global configuration variables.

#!/usr/bin/python

def init():
	global DEBUG
	global LABELING
	global JOB_FREQ_HISTORY_DICT
	global JOB_TIME_HISTORY_DICT
	DEBUG = 0
	LABELING = 1
	JOB_FREQ_HISTORY_DICT = dict()
	JOB_TIME_HISTORY_DICT = dict()
