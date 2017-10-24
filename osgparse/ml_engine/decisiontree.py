from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import cross_val_predict
import numpy as np
import csv
import sys

class DecisionTree():
	def __init__(self):
		self.confusion_matrix = np.matrix([])
		self.y_test = np.array([])
		self.y_score = np.array([])

	def predict(self, df_train, df_test, labels):
		tree = DecisionTreeClassifier(criterion='entropy', max_depth=5, random_state=0)
		x_train = df_train.loc[:,df_train.columns != 'Class'].values
		y_train = df_train.loc[:,df_train.columns == 'Class'].values[:,0]
		x_test = df_test.loc[:,df_test.columns != 'Class'].values
		y_test = df_test.loc[:,df_test.columns == 'Class'].values[:,0]
		tree.fit(x_train, y_train)
		y_predict = tree.predict(x_test)
		self.confusion_matrix = confusion_matrix(y_test, y_predict, labels)

	def classify(self, df_train, df_test, labels):
		classifier = OneVsRestClassifier(DecisionTreeClassifier(criterion='entropy', max_depth=5, random_state=0))
		x_train = df_train.loc[:,df_train.columns != 'Class'].values
		y_train = df_train.loc[:,df_train.columns == 'Class'].values[:,0]
		print labels
		y_train = label_binarize(y_train, classes=labels)
		x_test = df_test.loc[:,df_test.columns != 'Class'].values
		y_test = df_test.loc[:,df_test.columns == 'Class'].values[:,0]
		y_test = label_binarize(y_test, classes=labels)
		self.y_test = y_test
		self.y_score = classifier.fit(x_train, y_train).predict_proba(x_test)
		print self.y_score

	def crossval(self, df, cv, n_jobs):
		tree = DecisionTreeClassifier(criterion='entropy', max_depth=5, random_state=0)
		x = df.loc[:,df.columns != 'Class'].values
		y = df.loc[:,df.columns == 'Class'].values[:,0]
		return cross_val_score(estimator=tree, X=x, y=y, cv=cv, n_jobs=n_jobs)

	def crossmatrix(self, df, cv, n_jobs):
		tree = DecisionTreeClassifier(criterion='entropy', max_depth=5, random_state=0)
		x = df.loc[:,df.columns != 'Class'].values
		y = df.loc[:,df.columns == 'Class'].values[:,0]
		print x
		print y
		y_pred = cross_val_predict(estimator=tree, X=x, y=y, cv=cv, n_jobs=n_jobs)
		return confusion_matrix(y, y_pred, labels=['Retire', 'Preemption', 'Recycle', 'Kill', 'NetworkIssue'])

	def get_confusion_matrix(self):
		return self.confusion_matrix

	def get_y_test(self):
		return self.y_test

	def get_y_score(self):
		return self.y_score
