# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Zhe Zhang, zzxuanyuan@gmail.com
#
# This module is part of failure analysis of OSG project and is released under
# the BSD License: https://opensource.org/licenses/BSD-3-Clause

from osgparse import cli
import osgparse.parser
import osgparse.lifecycle
import osgparse.formatter
import osgparse.recorder
import osgparse.constants

__version__ = '0.1.1'

def extract_date(snapshot_file):
	path_list = snapshot_file.split("/")
	fname = path_list[-1]
	tmp_list = fname.split(".")
	date_list = tmp_list[0]
	date = date_list[0:2] + "/" + date_list[2:4] + "/" + date_list[6:8]
	print date
	return date
	
def format(**opts):
	snapshot_date_list = []
	snapshot_file_list = []
	with open(opts['filename'], 'r') as snapshot_files:
		for snapshot_file in snapshot_files:
			snapshot_file = snapshot_file.strip("\n")
			measure_date = extract_date(snapshot_file)
			snapshot_date_list.append(measure_date)
			snapshot_file_list.append(snapshot_file)
	osgparse.constants.init(snapshot_date_list)
	parser = osgparse.parser.Parser()
	generator = osgparse.lifecycle.LifecycleGenerator(osgparse.constants.JOB_FREQ_HISTORY_DICT, osgparse.constants.JOB_TIME_HISTORY_DICT)
	formatter = osgparse.formatter.LifecycleFormatter(osgparse.constants.JOB_FREQ_HISTORY_DICT, osgparse.constants.JOB_TIME_HISTORY_DICT, osgparse.constants.MEASURE_DATE_DICT)
	for file_path in snapshot_file_list:
		with open(file_path, 'r') as lines:
			for line in lines:
				snapshot = parser.read_line(line)
				finished_job_dict = generator.generate(snapshot)
				for l in finished_job_dict:
					formatted_job = formatter.format_lifecycle(finished_job_dict[l],snapshot.job_num,snapshot.job_num_resource_dict)
					formatted_job.formatted_dump()

def timeseries(**opts):
	snapshot_date_list = []
	snapshot_file_list = []
	with open(opts['filename'], 'r') as snapshot_files:
		for snapshot_file in snapshot_files:
			snapshot_file = snapshot_file.strip("\n")
			measure_date = extract_date(snapshot_file)
			snapshot_date_list.append(measure_date)
			snapshot_file_list.append(snapshot_file)
	osgparse.constants.init(snapshot_date_list)
	parser = osgparse.parser.Parser()
	recorder = osgparse.recorder.TimeseriesRecorder(osgparse.constants.MEASURE_DATE_DICT)
	for file_path in snapshot_file_list:
		with open(file_path, 'r') as lines:
			for line in lines:
				snapshot = parser.read_line(line)
				recorder.record(snapshot)
	recorder.dump(opts['outfile'])
