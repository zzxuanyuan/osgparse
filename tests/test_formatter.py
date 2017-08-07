# -*- coding: utf-8 -*-

import os
import sys
import pytest
import filecmp

from cStringIO import StringIO

import osgparse
import osgparse.lifecycle

import osgparse.constants

def print_dict(dictionary):
	result = ""
	cnt = 0
	for key, value in sorted(dictionary.iteritems()):
		cnt += 1
		if cnt == len(dictionary):
			result += "['" + key + "'" + ":" + str(value) + "]"
		else:
			result += "['" + key + "'" + ":" + str(value) + "], "
	return result

def test_lifecycle_fin_jobs_labeling():
	osgparse.constants.init()
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/three_snapshots"
	tmp_path = dir_path + "/files/result_three_snapshots_labeling.ini"

	parser = osgparse.parser.Parser()
	generator = osgparse.lifecycle.LifecycleGenerator(osgparse.constants.JOB_FREQ_HISTORY_DICT, osgparse.constants.JOB_TIME_HISTORY_DICT)
	formatter = osgparse.formatter.LifecycleFormatter(osgparse.constants.JOB_FREQ_HISTORY_DICT, osgparse.constants.JOB_TIME_HISTORY_DICT)
	old_stdout = sys.stdout
	sys.stdout = tmpstdout = StringIO()
	with open(tmp_path, "w") as o:
		with open(file_path, "r") as lines:
			for line in lines:
				snapshot = parser.read_line(line)
				finished_job_dict = generator.generate(snapshot)
				if not finished_job_dict:
					print "No job finishes."
				else:
					for l in sorted(finished_job_dict):
						formatted_job = formatter.format_lifecycle(finished_job_dict[l],snapshot.job_num)
						formatted_job.dump()
			formatter.dump()
			print "global freq dict : ", print_dict(osgparse.constants.JOB_FREQ_HISTORY_DICT)
			print "global time dict : ", print_dict(osgparse.constants.JOB_TIME_HISTORY_DICT)
			o.write(tmpstdout.getvalue())
	expect_path = dir_path + "/files/expected_three_snapshots_labeling.ini"
#	assert filecmp.cmp(tmp_path,expect_path)
#	os.remove(tmp_path)
"""
def test_lifecycle_fin_jobs_with_multiple_items_labeling():
	osgparse.constants.init()
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/four_snapshots_finish_job_with_multiple_items"
	tmp_path = dir_path + "/files/result_four_snapshots_finish_job_with_multiple_items_labeling.ini"

	generator = osgparse.lifecycle.LifecycleGenerator()
	parser = osgparse.parser.Parser()
        old_stdout = sys.stdout
        sys.stdout = tmpstdout = StringIO()
	with open(tmp_path, "w") as o:
		with open(file_path, "r") as lines:
			for line in lines:
				snapshot = parser.read_line(line)
				finished_job_dict = generator.generate(snapshot)
				if not finished_job_dict:
					print "No job finishes."
				else:
					for l in sorted(finished_job_dict):
						finished_job_dict[l].dump()
			o.write(tmpstdout.getvalue())

	expect_path = dir_path + "/files/expected_four_snapshots_finish_job_with_multiple_items_labeling.ini"
	assert filecmp.cmp(tmp_path,expect_path)
	os.remove(tmp_path)
"""
