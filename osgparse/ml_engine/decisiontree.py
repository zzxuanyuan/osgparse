from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
import numpy as np

class DecisionTree():
	def __init__(self):
		self.confusion_matrix = np.matrix([])

	def predict(self, df_train, df_test, labels):
		tree = DecisionTreeClassifier(criterion='entropy', max_depth=3, random_state=0)
		x_train = df_train.loc[:,df_train.columns != 'Class'].values
		y_train = df_train.loc[:,df_train.columns == 'Class'].values[:,0]
		x_test = df_test.loc[:,df_test.columns != 'Class'].values
		y_test = df_test.loc[:,df_test.columns == 'Class'].values[:,0]
		tree.fit(x_train, y_train)
		y_predict = tree.predict(x_test)
		self.confusion_matrix = confusion_matrix(y_test, y_predict, labels)
	
	def get_confusion_matrix(self):
		return self.confusion_matrix
