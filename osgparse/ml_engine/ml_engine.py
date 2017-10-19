import pandas as pd
import numpy as np
import decisiontree
import svm
import randomforest
import knn
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
		print "names = ", names
		if model == 'DecisionTree':
			print "model is decision tree"
			self.model = decisiontree.DecisionTree()
		elif model == 'SVM':
			self.model = svm.SVM()
		elif model == 'RandomForest':
			print "model is random forest"
			self.model = randomforest.RandomForest()
		elif model == 'KNN':
			self.model = knn.KNN()
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
		if len(self.names) == 0:
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
				df_test = df_test_each[self.attributes]
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
		print self.confusion_matrix

	def crossval(self, df_raw, cv=10, n_jobs=4):
		if len(self.names) == 1:
			name = self.names[0]
			df_each = df_raw[df_raw[self.split]==name]
			df = df_each[self.attributes]
		else:
			df = df_raw[self.attributes]
		return self.model.crossval(df, cv, n_jobs)

	def _crossmatrix(self, df_each, cv=10, n_jobs=4):
		df = df_each[self.attributes]
		return self.model.crossmatrix(df, cv, n_jobs)

	def crossmatrix(self, df_raw, cv=10, n_jobs=4):
		cross_matrix = np.matrix([])
		for name in self.names:
			print "cross_matrix at ", name
			df_each = df_raw[df_raw[self.split]==name]
			if len(df_each.index) < 2*cv:
				continue
			if cross_matrix.size == 0:
				each_matrix = self._crossmatrix(df_each, cv=10, n_jobs=4)
				print "each_matrix: "
				print each_matrix
				cross_matrix = each_matrix
			else:
				each_matrix = self._crossmatrix(df_each, cv=10, n_jobs=4)
				print "each_matrix: "
				print each_matrix
				cross_matrix += each_matrix
		return cross_matrix

	def get_confusion_matrix(self):
		return self.confusion_matrix

	def get_confusion_matrix_dict(self, name):
		return self.confusion_matrix_dict[name]
