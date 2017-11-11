import pandas as pd
import numpy as np
import decisiontree
import svm
import randomforest
import knn
import copy

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp

class MLEngine():

	def __init__(self, labels, names=[], model='DecisionTree', split='ResourceNames'):
		self.confusion_matrix = np.matrix([])
		self.y_test_total = np.array([])
		self.y_score_total = np.array([])
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
			self.y_test_total_dict = dict()
			self.y_score_total_dict = dict()
			for name in self.names:
				self.confusion_matrix_dict[name] = np.matrix([])
				self.y_test_total_dict[name] = np.array([])
				self.y_score_total_dict[name] = np.array([])

	def predict(self, df_train_raw, df_test_raw):
#		print "begin predict : "
#		print "confusion_matrix_dict[MWT2]: ",self.confusion_matrix_dict['MWT2']
		if len(self.names) == 0:
			df_train = df_train_raw[self.attributes]
			df_test = df_test_raw[self.attributes]
			self.model.predict(df_train, df_test)
			if self.confusion_matrix.size == 0:
				self.confusion_matrix = copy.deepcopy(self.model.get_confusion_matrix())
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
					self.confusion_matrix_dict[name] = copy.deepcopy(self.model.get_confusion_matrix())
					if self.confusion_matrix.size == 0:
						self.confusion_matrix = copy.deepcopy(self.model.get_confusion_matrix())
					else:
						self.confusion_matrix += self.model.get_confusion_matrix()
				else:
#					print "add : ", self.confusion_matrix_dict[name]
#					print "and ", self.model.get_confusion_matrix()
					self.confusion_matrix_dict[name] += self.model.get_confusion_matrix()
					if self.confusion_matrix.size == 0:
						self.confusion_matrix = copy.deepcopy(self.model.get_confusion_matrix())
					else:
						self.confusion_matrix += self.model.get_confusion_matrix()

#				if name == 'MWT2':
#				print "later: ",self.confusion_matrix_dict['MWT2']
		print self.confusion_matrix

	def classify(self, df_train_raw, df_test_raw):
		if len(self.names) == 0:
			df_train = df_train_raw[self.attributes]
			df_test = df_test_raw[self.attributes]
			self.model.classify(df_train, df_test)
			if self.y_score_total.size == 0 and self.y_test_total.size == 0:
				self.y_test_total = copy.deepcopy(self.model.get_y_test())
				self.y_score_total = copy.deepcopy(self.model.get_y_score())
			else:
				self.y_test_total = np.concatenate((self.y_test_total, self.model.get_y_test()), axis=0)
				self.y_score_total = np.concatenate((self.y_score_total, self.model.get_y_score()), axis=0)
		else:
			for name in self.names:
				df_train_each = df_train_raw[df_train_raw[self.split]==name]
				df_test_each = df_test_raw[df_test_raw[self.split]==name]
				df_train = df_train_each[self.attributes]
				df_test = df_test_each[self.attributes]
				if df_train.size == 0 or df_test.size == 0:
					continue
				self.model.classify(df_train, df_test, self.labels)
				if self.y_test_total_dict[name].size == 0 and self.y_score_total_dict[name].size == 0:
					self.y_test_total_dict[name] = copy.deepcopy(self.model.get_y_test())
					self.y_score_total_dict[name] = copy.deepcopy(self.model.get_y_score())
					if self.y_test_total.size == 0 and self.y_score_total.size == 0:
						self.y_test_total = copy.deepcopy(self.model.get_y_test())
						self.y_score_total = copy.deepcopy(self.model.get_y_score())
					else:
						self.y_test_total = np.concatenate((self.y_test_total, self.model.get_y_test()), axis=0)
						self.y_score_total = np.concatenate((self.y_score_total, self.model.get_y_score()), axis=0)
				else:
					self.y_test_total_dict[name] = np.concatenate((self.y_test_total_dict[name], self.model.get_y_test()), axis=0)
					self.y_score_total_dict[name] = np.concatenate((self.y_score_total_dict[name], self.model.get_y_score()), axis=0)
					if self.y_test_total.size == 0 and self.y_score_total.size == 0:
						self.y_test_total = copy.deepcopy(self.model.get_y_test())
						self.y_score_total = copy.deepcopy(self.model.get_y_score())
					else:
						self.y_test_total = np.concatenate((self.y_test_total, self.model.get_y_test()), axis=0)
						self.y_score_total = np.concatenate((self.y_score_total, self.model.get_y_score()), axis=0)
				print "test shape ", self.y_test_total.shape
				print "score shape ", self.y_score_total.shape
		print (self.y_test_total, self.y_score_total)
		"""
		# Compute ROC curve and ROC area for each class
		fpr = dict()
		tpr = dict()
		roc_auc = dict()
		print self.y_test_total.shape
		for i in range(5):
			fpr[i], tpr[i], _ = roc_curve(self.y_test_total[:, i], self.y_score_total[:, i])
			roc_auc[i] = auc(fpr[i], tpr[i])
			plt.figure()
			lw = 2
			plt.plot(fpr[i], tpr[i], color='darkorange', lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[i])
			plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
			plt.xlim([0.0, 1.0])
			plt.ylim([0.0, 1.05])
			plt.xlabel('False Positive Rate')
			plt.ylabel('True Positive Rate')
			plt.title('Receiver operating characteristic example')
			plt.legend(loc="lower right")
			plt.show()
		# Compute micro-average ROC curve and ROC area
		fpr["micro"], tpr["micro"], _ = roc_curve(self.y_test_total.ravel(), self.y_score_total.ravel())
		roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
		plt.figure()
		lw = 2
		plt.plot(fpr["micro"], tpr["micro"], color='darkorange', lw=lw, label='ROC curve (area = %0.2f)' % roc_auc["micro"])
		plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
		plt.xlim([0.0, 1.0])
		plt.ylim([0.0, 1.05])
		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.title('Receiver operating characteristic example')
		plt.legend(loc="lower right")
		plt.show()
		"""

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

	def get_y_test_total(self):
		return self.y_test_total

	def get_y_score_total(self):
		return self.y_score_total

	def get_y_test_total_dict(self, name):
		return self.y_test_total_dict[name]

	def get_y_score_total_dict(self, name):
		return self.y_score_total_dict[name]
