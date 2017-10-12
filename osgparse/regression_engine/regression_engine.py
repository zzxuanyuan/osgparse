from collections import Counter
import preemption_regressor
import pandas as pd
import numpy as np
import copy

class RegressionEngine():
	""" RegressionEngine takes labels and names as input and generate training data and test data which are going to parse into predict later """
	def __init__(self, labels=np.array([]), names=np.array([]), regression_model='PreemptionRegression', split='ResourceNames'):
		print "labels = ", labels
		print "names = ", names
		self.fault_tolerance = Counter(dict())
		self.fault_tolerance_dict = dict(Counter(dict()))
		for name in names:
			self.fault_tolerance_dict[name] = Counter(dict()) # right now fault_tolerance_dict only for resource names.
		self.labels = labels
		self.names = names
		if regression_model == 'PreemptionRegression':
			self.regression_model = 'PreemptionRegression'
			self.target = 'DesktopEndDateMinute'
			self.attributes = ['DesktopStartDateMinute', 'DesktopEndDateMinute']
			self.regressor = preemption_regressor.PreemptionRegressor(self.attributes, self.target)
		if split == "" or split == None:
			self.split = None
		else:
			self.split = split

	
	def predict(self, df_train_raw, df_test_raw, cur_desktop_time):
		print "in predict"
		if self.regression_model == 'PreemptionRegression':
			print "preemption regression"
			self._predict_preemption_regression(df_train_raw, df_test_raw, cur_desktop_time)

	def _predict_preemption_regression(self, df_train_raw, df_test_raw, cur_desktop_time):
		df_train_raw = df_train_raw[df_train_raw['Class'].isin(self.labels)]
		df_test_raw = df_test_raw[df_test_raw['Class'].isin(self.labels)]
		if self.names.size == 0:
			df_train = df_train_raw[self.attributes]
			df_test = df_test_raw[self.attributes]
			self.regressor.predict(df_train, df_test, cur_desktop_time)
			if self.fault_tolerance.size == 0:
				self.fault_tolerance = Counter(self.regressor.get_fault_tolerance())
			else:
				self.fault_tolerance += Counter(self.regressor.get_fault_tolerance())
		else:
			print "self.names = ", self.names
			for name in self.names:
				print "name = ", name
				df_train_each = df_train_raw[df_train_raw[self.split]==name]
				df_test_each = df_test_raw[df_test_raw[self.split]==name]
				df_train = df_train_each[self.attributes]
				df_test = df_test_each[self.attributes]
				if df_train.size == 0 or df_test.size == 0:
					continue
				self.regressor.predict(df_train, df_test, cur_desktop_time)
				if len(self.fault_tolerance_dict[name]) == 0:
					self.fault_tolerance_dict[name] = Counter(self.regressor.get_fault_tolerance())
					if len(self.fault_tolerance) == 0:
						self.fault_tolerance = Counter(self.regressor.get_fault_tolerance())
					else:
						self.fault_tolerance += Counter(self.regressor.get_fault_tolerance())
				else:
					self.fault_tolerance_dict[name] += Counter(self.regressor.get_fault_tolerance())
					if len(self.fault_tolerance) == 0:
						self.fault_tolerance = Counter(self.regressor.get_fault_tolerance())
					else:
						self.fault_tolerance += Counter(self.regressor.get_fault_tolerance())

	def get_fault_tolerance(self):
		return self.fault_tolerance

	def get_fault_tolerance_dict(self, name):
		return self.fault_tolerance_dict[name]

	def dump_fault_tolerance(self):
		print self.fault_tolerance
