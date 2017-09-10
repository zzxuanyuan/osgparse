import decisiontree_regressor
import randomforest_regressor
import pandas as pd
import numpy as np
import copy

class RegressionEngine():

	def __init__(self, names=[], regressor='DecisionTree', split='ResourceNames'):
		self.fault_tolerance_rate = []
		self.fault_tolerance_rate_dict = dict()
		for name in names:
			self.fault_tolerance_rate_dict[name] = []
#		self.attributes = ['MaxRetireTime', 'MaxKillTime', 'TotalJobNumber', 'ResourceJobNumber', 'DesktopStartDate', 'DesktopStartHour', 'DesktopStartMinute',
#				'DesktopStartHourMinute', 'DesktopStartDateMinute', 'NumberOfHost', 'SiteNames', 'ResourceNames', 'EntryNames', 'JobStartTime', 'PreemptionFrequency',
#				'Class']
#		self.attributes = ['MaxRetireTime', 'MaxKillTime', 'TotalJobNumber', 'ResourceJobNumber', 'DesktopStartDateMinute', 'NumberOfHost', 'JobStartTime', 'PreemptionFrequency', 'Duration']
		self.attributes = ['MaxRetireTime', 'MaxKillTime', 'DesktopStartDateMinute', 'NumberOfHost', 'JobStartTime', 'PreemptionFrequency', 'Duration']
		self.names = names
		if regressor == 'DecisionTree':
			self.regressor = decisiontree_regressor.CustomizedDecisionTreeRegressor()
		elif regressor == 'RandomForest':
			self.regressor = randomforest_regressor.CustomizedRandomForestRegressor()
		if split == "" or split == None:
			self.split = None
		else:
			self.split = split

	def predict(self, df_train_raw, df_test_raw):
		if self.names.size == 0:
			df_train = df_train_raw[self.attributes]
			df_test = df_test_raw[self.attributes]
			self.regressor.predict(df_train, df_test)
			if self.fault_tolerance_rate.size == 0:
				self.fault_tolerance_rate = self.regressor.get_fault_tolerance_rate()
			else:
				self.fault_tolerance_rate += self.regressor.get_fault_tolerance_rate()
		else:
			for name in self.names:
				df_train_each = df_train_raw[df_train_raw[self.split]==name]
				df_test_each = df_test_raw[df_test_raw[self.split]==name]
				df_train = df_train_each[self.attributes]
				df_test = df_train_each[self.attributes]
				if df_train.size == 0 or df_test.size == 0:
					continue
#				if name == 'MWT2':
#					print df_test.index
				self.regressor.predict(df_train, df_test)
#				if name == 'MWT2':
#					print "origin confusion_matrix: ",self.model.get_confusion_matrix()
#					print "origin confusion_matrix_dict[MWT2]: ",self.confusion_matrix_dict[name]
				if len(self.fault_tolerance_rate_dict[name]) == 0:
					self.fault_tolerance_rate_dict[name] = self.regressor.get_fault_tolerance_rate()
					if len(self.fault_tolerance_rate) == 0:
						self.fault_tolerance_rate = self.regressor.get_fault_tolerance_rate()
					else:
						self.fault_tolerance_rate += self.regressor.get_fault_tolerance_rate()
				else:
#					print "add : ", self.confusion_matrix_dict[name]
#					print "and ", self.model.get_confusion_matrix()
					self.fault_tolerance_rate_dict[name] += self.regressor.get_fault_tolerance_rate()
					if len(self.fault_tolerance_rate) == 0:
						self.fault_tolerance_rate = self.regressor.get_fault_tolerance_rate()
					else:
						self.fault_tolerance_rate += self.regressor.get_fault_tolerance_rate()
#				if name == 'MWT2':
#				print "later: ",self.confusion_matrix_dict['MWT2']

	def get_fault_tolerance_rate(self):
		return self.fault_tolerance_rate

	def get_fault_tolerance_rate_dict(self, name):
		return self.fault_tolerance_rate_dict[name]

	def dump_fault_tolerance_rate(self):
		r_1p = [i for i in self.fault_tolerance_rate if i < 0.01]
		r_5p = [i for i in self.fault_tolerance_rate if i < 0.05]
		r_10p = [i for i in self.fault_tolerance_rate if i < 0.1]
		r_20p = [i for i in self.fault_tolerance_rate if i < 0.2]
		r_30p = [i for i in self.fault_tolerance_rate if i < 0.3]
		r_40p = [i for i in self.fault_tolerance_rate if i < 0.4]
		r_50p = [i for i in self.fault_tolerance_rate if i < 0.5]
		r_60p = [i for i in self.fault_tolerance_rate if i < 0.6]
		r_70p = [i for i in self.fault_tolerance_rate if i < 0.7]
		r_80p = [i for i in self.fault_tolerance_rate if i < 0.8]
		r_90p = [i for i in self.fault_tolerance_rate if i < 0.9]
		r_100p = [i for i in self.fault_tolerance_rate if i < 1.0]
		r_500p = [i for i in self.fault_tolerance_rate if i < 5.0]
		r_1000p = [i for i in self.fault_tolerance_rate if i < 10.0]
		print "1% : ", len(r_1p)*1.0/len(self.fault_tolerance_rate)
		print "5% : ", len(r_5p)*1.0/len(self.fault_tolerance_rate)
		print "10% : ", len(r_10p)*1.0/len(self.fault_tolerance_rate)
		print "20% : ", len(r_20p)*1.0/len(self.fault_tolerance_rate)
		print "30% : ", len(r_30p)*1.0/len(self.fault_tolerance_rate)
		print "40% : ", len(r_40p)*1.0/len(self.fault_tolerance_rate)
		print "50% : ", len(r_50p)*1.0/len(self.fault_tolerance_rate)
		print "60% : ", len(r_60p)*1.0/len(self.fault_tolerance_rate)
		print "70% : ", len(r_70p)*1.0/len(self.fault_tolerance_rate)
		print "80% : ", len(r_80p)*1.0/len(self.fault_tolerance_rate)
		print "90% : ", len(r_90p)*1.0/len(self.fault_tolerance_rate)
		print "100%: ", len(r_100p)*1.0/len(self.fault_tolerance_rate)
		print "500%: ", len(r_500p)*1.0/len(self.fault_tolerance_rate)
		print "1000%: ", len(r_1000p)*1.0/len(self.fault_tolerance_rate)
