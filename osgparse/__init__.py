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
import osgparse.plotter
import osgparse.slidingwindow
import osgparse.constants
import osgparse.ml_engine.ml_engine
import osgparse.regression_engine.regression_engine
import osgparse.utils
import osgparse.filter_engine

import pandas as pd

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
	file_to_write = open(opts['outfile'], 'w')
	column_names_string = "JobId" + "," + "Duration" + "," + "MaxRetireTime" + "," + "MaxKillTime" + "," + "TotalJobNumber" + "," + "ResourceJobNumber" + "," + "DesktopStartDate" + "," + "DesktopStartHour" + "," + "DesktopStartMinute" + "," + "DesktopStartHourMinute" + "," + "DesktopStartDateMinute" + "," + "DesktopMeanDate" + "," + "DesktopMeanHour" + "," + "DesktopMeanMinute" + "," + "DesktopMeanHourMinute" + "," + "DesktopMeanDateMinute" + "," + "DesktopEndDate" + "," + "DesktopEndHour" + "," + "DesktopEndMinute" + "," + "DesktopEndHourMinute" + "," + "DesktopEndDateMinute" + "," + "NumberOfHost" + "," + "SiteNames" + "," + "ResourceNames" + "," + "EntryNames" + "," + "JobStartTime" + "," + "JobEndTime" + "," + "PreemptionFrequency" + "," + "Class" + "\n"
	file_to_write.write(column_names_string)
	for file_path in snapshot_file_list:
		with open(file_path, 'r') as lines:
			for line in lines:
				snapshot = parser.read_line(line)
				finished_job_dict = generator.generate(snapshot)
				for l in finished_job_dict:
					formatted_job = formatter.format_lifecycle(finished_job_dict[l],snapshot.job_num,snapshot.job_num_resource_dict)
					osgparse.constants.JOB_TIME_HISTORY_DICT[l] = finished_job_dict[l].daemon_start_set
					formatted_job.formatted_dump(file_to_write)
	file_to_write.close()

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

def plot(**opts):
	snapshot_date_list = []
	with open(opts['filename'], 'r') as snapshot_files:
		for snapshot_file in snapshot_files:
			snapshot_file = snapshot_file.strip("\n")
			measure_date = extract_date(snapshot_file)
			snapshot_date_list.append(measure_date)
	osgparse.constants.init(snapshot_date_list)
	plotter = osgparse.plotter.Plotter(osgparse.constants.MEASURE_DATE_DICT,opts['jobinstances'],opts['timeseries'])
	if opts['plottype'] == 'timeseries':
		plotter.plot_time_series(opts['resource'], opts['label'])
	elif opts['plottype'] == 'duration':
		plotter.plot_duration(opts['resource'], opts['label'])
	elif opts['plottype'] == 'timepoint':
		plotter.plot_time_point(opts['resource'], opts['timepoint'])

def classify(**opts):
	snapshot_date_list = []
	window = osgparse.slidingwindow.SlidingWindow(opts['jobinstances'])
	res = 0
	labels = window.get_values('Class')
	names = window.get_values('ResourceNames')
	mle = osgparse.ml_engine.ml_engine.MLEngine(labels, names, 'DecisionTree', 'ResourceNames')
	data_tuple = (pd.DataFrame(), pd.DataFrame())
	while(1):
		data_tuple = window.slide()
		if data_tuple == "EOF":
			break
		data_train = data_tuple[0]
		data_test = data_tuple[1]
		mle.predict(data_train, data_test)
#		print "in __init__"
#		print mle.get_confusion_matrix_dict('MWT2')
	confusion_matrix = mle.get_confusion_matrix()
	print confusion_matrix

def predict(**opts):
	snapshot_date_list = []
	window = osgparse.slidingwindow.SlidingWindow(opts['jobinstances'])
	res = 0
	names = window.get_values('ResourceNames')
	regressor = osgparse.regression_engine.regression_engine.RegressionEngine(names, opts['regressionmodel'], 'ResourceNames')
	data_tuple = (pd.DataFrame(), pd.DataFrame())
	while(1):
		data_tuple = window.slide()
		if data_tuple == "EOF":
			break
		data_train = data_tuple[0]
		data_test = data_tuple[1]
		regressor.predict(data_train, data_test)
	fault_tolerance_rate = regressor.get_fault_tolerance_rate()
	regressor.dump_fault_tolerance_rate()

def filter(**opts):
	ftr = osgparse.filter_engine.FilterEngine()
	if opts['exclude']:
		print "exclusive exists"
		ftr.filter_exclusive(opts['jobinstances'],opts['outfile'],opts['exclude'])
	elif opts['include']:
		print "inclusive exists"
		ftr.filter_inclusive(opts['jobinstances'],opts['outfile'],opts['include'])
	print "nothing exists"

def changelabel(**opts):
	osgparse.utils.changelabel(opts['jobinstances'],opts['outfile'],5)
