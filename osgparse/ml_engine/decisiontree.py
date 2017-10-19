from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import cross_val_predict
import numpy as np

class DecisionTree():
	def __init__(self):
		self.confusion_matrix = np.matrix([])

	def predict(self, df_train, df_test, labels):
		tree = DecisionTreeClassifier(criterion='entropy', max_depth=5, random_state=0)
		x_train = df_train.loc[:,df_train.columns != 'Class'].values
		y_train = df_train.loc[:,df_train.columns == 'Class'].values[:,0]
		x_test = df_test.loc[:,df_test.columns != 'Class'].values
		y_test = df_test.loc[:,df_test.columns == 'Class'].values[:,0]
		tree.fit(x_train, y_train)
		y_predict = tree.predict(x_test)
		self.confusion_matrix = confusion_matrix(y_test, y_predict, labels)

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
