# This file does regression test using Random Forest Regression.
# The input file should be insert_total_jobs.csv that contains total jobs info.

import matplotlib.pyplot as plt
import math
import sys
import pandas as pd
import numpy as np

class SlidingWindow:

	def __init__(self, job_instances_file, attribute = "DesktopEndDateMinute", train_window_size = 20, test_window_size = 5, skip = False, skip_total_run = 100):
		self.df = pd.read_csv(job_instances_file, header=0)
		self.attribute = attribute
		if attribute != "DesktopEndDateMinute":
			print "ERROR: attribute is not DesktopEndDateMinute"
			return -1
		self.value_counts = self.df[attribute].value_counts()
		self.index_list = sorted(self.value_counts.index)
		self.skip = skip
		if skip is True:
			self.skip_total_run = skip_total_run
			self.index_position = 0
			self.skip_distance = len(self.index_list)/skip_total_run
			print self.index_list
			print "self.index_list's length = ", len(self.index_list)
			print "self.skip_distance = ", self.skip_distance
		self.train_window_size = train_window_size
		self.test_window_size = test_window_size
		self.cur_train_attr_start = None
		self.cur_train_attr_end = None
		self.cur_test_attr_start = None
		self.cur_test_attr_end = None
		self.cur_train_index_start = None
		self.cur_train_index_end = None
		self.cur_test_index_start = None
		self.cur_test_index_end = None
		self.cur_train_line_start = None
		self.cur_train_line_end = None
		self.cur_test_line_start = None
		self.cur_test_line_end = None
		self.next_window_index = None
		self.next_window_line_start = None
		self.df_train = None
		self.df_test = None
#		self.machine_learning_engine = osgparse.mlengine.MachineLearningEngine()
#		self.regression_engine = osg

	def slide_depreciated(self):
		if self.cur_train_attr_start == None and self.cur_train_attr_end == None and self.cur_test_attr_start == None and self.cur_test_attr_end == None:
			self.cur_train_index_start = 0
			self.cur_train_attr_start = self.index_list[0]
			self.cur_train_line_start = 0
			self.next_window_line_start = 0
		else:
			# find right attrribute positions to avoid reaching the end of data
			self.cur_train_index_start += self.test_window_size
			self.cur_train_attr_start = self.index_list[self.cur_train_index_start]
			self.cur_train_line_start = self.next_window_line_start

		self.cur_train_index_end = self.cur_train_index_start + self.train_window_size - 1
		self.cur_test_index_start = self.cur_train_index_end + 1
		self.cur_test_index_end = self.cur_test_index_start + self.test_window_size - 1
		if self.cur_test_index_end >= len(self.index_list):
			print "Reach the end of DataFrame!"
			return "EOF"
		self.cur_train_attr_end = self.index_list[self.cur_train_index_end]
		self.cur_test_attr_start = self.index_list[self.cur_test_index_start]
		self.cur_test_attr_end = self.index_list[self.cur_test_index_end]
		accumulate_line = 0
		self.next_window_index = self.cur_train_index_start + self.test_window_size
		for idx in range(self.cur_train_index_start, self.cur_train_index_end + 1):
			if idx == self.next_window_index:
				self.next_window_line_start += accumulate_line
			accumulate_line += self.value_counts[self.index_list[idx]]
		self.cur_train_line_end = self.cur_train_line_start + accumulate_line - 1
		self.cur_test_line_start = self.cur_train_line_end + 1
		accumulate_line = 0
		for idx in range(self.cur_test_index_start, self.cur_test_index_end + 1):
			accumulate_line += self.value_counts[self.index_list[idx]]
		self.cur_test_line_end = self.cur_test_line_start + accumulate_line - 1
		self.df_train = self.df[self.cur_train_line_start:self.cur_train_line_end+1]
		self.df_test = self.df[self.cur_test_line_start:self.cur_test_line_end+1]

		return (self.df_train, self.df_test)

	def slide(self):
		if self.cur_train_attr_start == None and self.cur_train_attr_end == None and self.cur_test_attr_start == None and self.cur_test_attr_end == None:
			self.cur_train_index_start = 0
			self.cur_train_attr_start = self.index_list[0]
			self.cur_train_line_start = 0
			self.next_window_line_start = 0
		else:
			# find right attrribute positions to avoid reaching the end of data
			if self.skip is True:
				print "self_cur_train_index_start = ", self.cur_train_index_start
				self.cur_train_index_start += self.skip_distance
#				if self.cur_train_index_start >= len(self.index_list):
#					print "Reach the end"
#					return "EOF"
				self.cur_train_attr_start = self.index_list[self.cur_train_index_start]
				print "attribute = ", self.attribute
				print "self.cur_train_attr_start = ", self.cur_train_attr_start
				self.cur_train_line_start = self.df[self.df[self.attribute]==self.cur_train_attr_start].index[0]
			else:
				self.cur_train_index_start += self.test_window_size
				self.cur_train_attr_start = self.index_list[self.cur_train_index_start]
				self.cur_train_line_start = self.next_window_line_start

		self.cur_train_index_end = self.cur_train_index_start + self.train_window_size - 1
		self.cur_test_index_start = self.cur_train_index_end + 1
		self.cur_test_index_end = self.cur_test_index_start + self.test_window_size - 1
		if self.cur_test_index_end >= len(self.index_list):
			print "Reach the end of DataFrame!"
			return "EOF"
		self.cur_train_attr_end = self.index_list[self.cur_train_index_end]
		self.cur_test_attr_start = self.index_list[self.cur_test_index_start]
		self.cur_test_attr_end = self.index_list[self.cur_test_index_end]
		print self.cur_train_attr_start, self.cur_train_attr_end, self.cur_test_attr_start, self.cur_test_attr_end
		accumulate_line = 0
		self.next_window_index = self.cur_train_index_start + self.test_window_size
		for idx in range(self.cur_train_index_start, self.cur_train_index_end + 1):
			if idx == self.next_window_index:
				self.next_window_line_start += accumulate_line
			accumulate_line += self.value_counts[self.index_list[idx]]
		self.cur_train_line_end = self.cur_train_line_start + accumulate_line - 1
		self.cur_test_line_start = self.cur_train_line_end + 1
		accumulate_line = 0
		for idx in range(self.cur_test_index_start, self.cur_test_index_end + 1):
			accumulate_line += self.value_counts[self.index_list[idx]]
		self.cur_test_line_end = self.cur_test_line_start + accumulate_line - 1
		self.df_train = self.df[self.cur_train_line_start:self.cur_train_line_end+1]
#		self.df_test = self.df[self.cur_test_line_start:self.cur_test_line_end+1]
		self.df_test = self.df.loc[self.cur_test_line_start:].query('DesktopStartDateMinute <= @self.cur_test_attr_start and DesktopEndDateMinute > @self.cur_test_attr_start')
		if self.attribute != "DesktopEndDateMinute":
			print "ERROR: attribute is no damn DesktopEndDateMinute!"
			return -1
		return (self.df_train, self.df_test)

	def get_values(self, attribute):
		return self.df[attribute].value_counts().index
