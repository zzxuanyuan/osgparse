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
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt

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
	elif opts['plottype'] == 'jobdistance':
		plotter.plot_job_distance(opts['resource'], opts['label'])
	elif opts['plottype'] == 'timepoint':
		plotter.plot_time_point(opts['resource'], opts['timepoint'])
	elif opts['plottype'] == 'desktoptime':
		plotter.plot_desktop_start_end_correlation(opts['resource'], opts['label'])
	elif opts['plottype'] == 'timediff':
		plotter.plot_time_diff(opts['resource'], opts['label'], opts['attr1'], opts['attr2'])
	elif opts['plottype'] == 'timediffretirekill':
		plotter.plot_time_diff_retire_kill(opts['resource'])
	elif opts['plottype'] == 'timemaxretirekill':
		plotter.plot_time_max_retire_kill(opts['resource'])
	elif opts['plottype'] == 'maxtime':
		plotter.plot_max_retire_or_kill_time(opts['resource'], opts['label'], opts['attr'])
	elif opts['plottype'] == 'faulttolerance':
		plotter.plot_fault_tolerance(opts['resource'], opts['label'])
	elif opts['plottype'] == 'jobdistribution':
		plotter.plot_job_distribution(opts['attr'], opts['label'])
	elif opts['plottype'] == 'preemptiondistribution':
		plotter.plot_preemption_distribution()
	elif opts['plottype'] == 'duration':
		plotter.plot_duration(opts['resource'], opts['label'])

def classify(**opts):
	snapshot_date_list = []
	window = osgparse.slidingwindow.SlidingWindow(opts['jobinstances'], "DesktopEndDateMinute", 10000, 1000, True, 10)
	res = 0
	labels = window.get_values('Class')
	if opts['resource'] == None:
		names = window.get_values('ResourceNames')
	else:
		names = [opts['resource']]
	mle = osgparse.ml_engine.ml_engine.MLEngine(labels, names, opts['classificationmodel'], 'ResourceNames')
	data_tuple = (pd.DataFrame(), pd.DataFrame())
	while(1):
		data_tuple = window.slide()
		if data_tuple == "EOF":
			break
		data_train = data_tuple[0]
		data_test = data_tuple[1]
		mle.predict(data_train, data_test)
#		print "in __init__"
#		print "MWT2: ", mle.get_confusion_matrix_dict('MWT2')
	confusion_matrix = mle.get_confusion_matrix()
	print "printing final confusion matrix: "
	print confusion_matrix
	confusion_matrix_sum_dict = dict()
	for name in names:
		print "matrix: "
		print mle.get_confusion_matrix_dict(name)
		print "sum row : "
		print np.sum(mle.get_confusion_matrix_dict(name), axis=1)
		if mle.get_confusion_matrix_dict(name).size > 0:
			sum_row = np.sum(mle.get_confusion_matrix_dict(name), axis=1)
			confusion_matrix_sum_dict[name] = sum_row[1] # 1 is the preemption index: the second row
		else:
			confusion_matrix_sum_dict[name] = 0
	for key, value in sorted(confusion_matrix_sum_dict.iteritems(), key=lambda (k,v): (v,k), reverse=True):
		print "printint confusion matrix for ", key, " : "
		print mle.get_confusion_matrix_dict(key)

def classify_roc(**opts):
	snapshot_date_list = []
	window = osgparse.slidingwindow.SlidingWindow(opts['jobinstances'], "DesktopEndDateMinute", 10000, 1000, True, 10)
	res = 0
	labels = window.get_values('Class')
	if opts['resource'] == None:
		names = window.get_values('ResourceNames')
	else:
		names = [opts['resource']]
	mle = osgparse.ml_engine.ml_engine.MLEngine(labels, names, opts['classificationmodel'], 'ResourceNames')
	data_tuple = (pd.DataFrame(), pd.DataFrame())
	while(1):
		data_tuple = window.slide()
		if data_tuple == "EOF":
			break
		data_train = data_tuple[0]
		data_test = data_tuple[1]
		mle.classify(data_train, data_test)
	y_test = mle.get_y_test_total()
	y_score = mle.get_y_score_total()
	# Compute ROC curve and ROC area for each class
	fpr = dict()
	tpr = dict()
	roc_auc = dict()
	for i in range(len(labels)):
		fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
		roc_auc[i] = auc(fpr[i], tpr[i])
		# Compute micro-average ROC curve and ROC area
		fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
		roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
	plt.figure()
	lw = 2
	for i in range(len(labels)):
		plt.plot(fpr[i], tpr[i], lw=lw, label=labels[i]+'(area = %0.2f)' % roc_auc[i])
	plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
	plt.xlim([0.0, 1.0])
	plt.ylim([0.0, 1.05])
	plt.xlabel('False Positive Rate')
	plt.ylabel('True Positive Rate')
	plt.title('ROC Curve of Different Classes')
	plt.legend(loc="lower right")
	file_name = 'roc.png'
	file_name = '/Users/zhezhang/osgparse/figures/' + file_name
	plt.savefig(file_name)
	plt.show()
	for name in names:
		fpr = dict()
		tpr = dict()
		roc_auc = dict()
		y_test_name = mle.get_y_test_total_dict(name)
		y_score_name = mle.get_y_score_total_dict(name)
		if y_test_name.size == 0 and y_score_name.size == 0:
			break
		for i in range(len(labels)):
			fpr[i], tpr[i], _ = roc_curve(y_test_name[:, i], y_score_name[:, i])
			roc_auc[i] = auc(fpr[i], tpr[i])
			# Compute micro-average ROC curve and ROC area
			fpr["micro"], tpr["micro"], _ = roc_curve(y_test_name.ravel(), y_score_name.ravel())
		plt.figure()
		lw = 2
		for i in range(len(labels)):
			plt.plot(fpr[i], tpr[i], lw=lw, label=labels[i]+'(area = %0.2f)' % roc_auc[i])
		plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
		plt.xlim([0.0, 1.0])
		plt.ylim([0.0, 1.05])
		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.title('ROC Curve of Different Classes')
		plt.legend(loc="lower right")
		file_name = name + '_roc.png'
		file_name = '/Users/zhezhang/osgparse/figures/' + file_name
		plt.savefig(file_name)
		plt.show()

def predict(**opts):
	snapshot_date_list = []
	window = osgparse.slidingwindow.SlidingWindow(opts['jobinstances'], "DesktopEndDateMinute", 20, 1)
	res = 0
	if opts['resource'] == None:
		names = window.get_values('ResourceNames')
	else:
		name_string = opts['resource']
		if name_string[0] != '[' and name_string[-1] != ']':
			names = [name_string]
		else:
			names = name_string[1:-1].split(',')
			for name in names:
				name = name.strip()
	names = np.array(names)
	if opts['label'] == None:
		labels = None
	else:
		label_string = opts['label']
		if label_string[0] != '[' and label_string[-1] != ']':
			labels = [label_string]
		else:
			labels = label_string[1:-1].split(',')
			for label in labels:
				label = label.strip()
	labels = np.array(labels)
	regressor = osgparse.regression_engine.regression_engine.RegressionEngine(labels, names, opts['regressionmodel'], 'ResourceNames')
	data_tuple = (pd.DataFrame(), pd.DataFrame(), None)
	while(1):
		data_tuple = window.slide()
		if data_tuple == "EOF":
			break
		data_train = data_tuple[0]
		data_test = data_tuple[1]
		cur_desktop_time = data_tuple[2]
		regressor.predict(data_train, data_test, cur_desktop_time)
		print "sample size = ", data_train.size
		fault_tolerance = regressor.get_fault_tolerance()
		print "fault_tolerance_rate size = ", len(fault_tolerance)
		print "cur_desktop_time = ", cur_desktop_time
		print regressor.get_fault_tolerance()
	fault_tolerance = regressor.get_fault_tolerance()
	print fault_tolerance

def crossval(**opts):
	df = pd.read_csv(opts['jobinstances'], header=0)
	if opts['label'] == None:
		labels = df['Class'].value_counts().index
	else:
		labels = opts['label']
	if opts['resource'] == None:
		names = df['ResourceNames'].value_counts().index
	else:
		names = [opts['resource']]
	mle = osgparse.ml_engine.ml_engine.MLEngine(labels, names, opts['classificationmodel'], 'ResourceNames')
	score = mle.crossval(df, 10, 4)
	confusion_matrix = mle.crossmatrix(df, 10, 4)
	print score
	print confusion_matrix

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

def increment0preemption(**opts):
	osgparse.utils.increment0preemption(opts['jobinstances'],opts['outfile'])
