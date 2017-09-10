import pandas as pd
import numpy as np
import decisiontree
import copy

class MLEngine():

	def __init__(self, labels, names=[], model='DecisionTree', split='ResourceNames'):
		self.confusion_matrix = np.matrix([])
#		self.attributes = ['MaxRetireTime', 'MaxKillTime', 'TotalJobNumber', 'ResourceJobNumber', 'DesktopStartDate', 'DesktopStartHour', 'DesktopStartMinute',
#				'DesktopStartHourMinute', 'DesktopStartDateMinute', 'NumberOfHost', 'SiteNames', 'ResourceNames', 'EntryNames', 'JobStartTime', 'PreemptionFrequency',
#				'Class']
		self.attributes = ['MaxRetireTime', 'MaxKillTime', 'TotalJobNumber', 'ResourceJobNumber', 'DesktopStartDateMinute', 'NumberOfHost', 'JobStartTime', 'PreemptionFrequency', 'Class']
		self.labels = labels
		print "labels = ", self.labels
		self.names = names
		if model == 'DecisionTree':
			self.model = decisiontree.DecisionTree()
		if split == "" or split == None:
			self.split = None
			self.confusion_matrix_dict = None
		else:
			self.split = split
			self.confusion_matrix_dict = dict()
			for name in self.names:
				self.confusion_matrix_dict[name] = np.matrix([])

	def predict(self, df_train_raw, df_test_raw):
#		print "begin predict : "
#		print "confusion_matrix_dict[MWT2]: ",self.confusion_matrix_dict['MWT2']
		if self.names.size == 0:
			df_train = df_train_raw[self.attributes]
			df_test = df_test_raw[self.attributes]
			self.model.predict(df_train, df_test)
			if self.confusion_matrix.size == 0:
				self.confusion_matrix = self.model.get_confusion_matrix()
			else:
				self.confusion_matrix += self.model.get_confusion_matrix()
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
				self.model.predict(df_train, df_test, self.labels)
#				if name == 'MWT2':
#					print "origin confusion_matrix: ",self.model.get_confusion_matrix()
#					print "origin confusion_matrix_dict[MWT2]: ",self.confusion_matrix_dict[name]
				if self.confusion_matrix_dict[name].size == 0:
					self.confusion_matrix_dict[name] = self.model.get_confusion_matrix()
					if self.confusion_matrix.size == 0:
						self.confusion_matrix = self.model.get_confusion_matrix()
					else:
						self.confusion_matrix += self.model.get_confusion_matrix()
				else:
#					print "add : ", self.confusion_matrix_dict[name]
#					print "and ", self.model.get_confusion_matrix()
					self.confusion_matrix_dict[name] += self.model.get_confusion_matrix()
					if self.confusion_matrix.size == 0:
						self.confusion_matrix = self.model.get_confusion_matrix()
					else:
						self.confusion_matrix += self.model.get_confusion_matrix()

#				if name == 'MWT2':
#				print "later: ",self.confusion_matrix_dict['MWT2']

	def get_confusion_matrix(self):
		return self.confusion_matrix

	def get_confusion_matrix_dict(self, name):
		return self.confusion_matrix_dict[name]
