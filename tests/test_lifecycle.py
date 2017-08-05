# -*- coding: utf-8 -*-

import os
import sys
import pytest
import filecmp

from cStringIO import StringIO

import osgparse
import osgparse.lifecycle

import osgparse.constants
"""
def test_lifecycle_fin_jobs():
	osgparse.constants.init()
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/three_snapshots"
	tmp_path = dir_path + "/files/result_item.ini"

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

	expect_path = dir_path + "/files/expected_three_snapshots.ini"
	assert filecmp.cmp(tmp_path,expect_path)
	os.remove(tmp_path)
"""
def test_lifecycle_fin_jobs_with_multiple_items():
	osgparse.constants.init()
	osgparse.constants.DEBUG = 1
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/three_snapshots_with_multiple_items"
	tmp_path = dir_path + "/files/result_item.ini"

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

	expect_path = dir_path + "/files/expected_three_snapshots_with_multiple_items.ini"
	osgparse.constants.DEBUG = 0
	assert filecmp.cmp(tmp_path,expect_path)
	os.remove(tmp_path)
