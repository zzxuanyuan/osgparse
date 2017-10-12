from sklearn.tree import DecisionTreeRegressor
import numpy as np

class CustomizedDecisionTreeRegressor:
	def __init__(self, target):
		self.target = target
		self.fault_tolerance_rate = []

	def predict(self, df_train, df_test):
		tree = DecisionTreeRegressor(max_depth=3)
		df_train = df_train[df_train[self.target]!=0]
		df_test = df_test[df_test[self.target]!=0]
		x_train = df_train.loc[:,df_train.columns != self.target].values
		y_train = df_train.loc[:,df_train.columns == self.target].values[:,0]
		x_test = df_test.loc[:,df_test.columns != self.target].values
		y_test = df_test.loc[:,df_test.columns == self.target].values[:,0]
		tree.fit(x_train, y_train)
		y_predict = tree.predict(x_test)
		y_diff = y_predict - y_test
		self.fault_tolerance_rate = [abs(a*1.0/b) for a,b in zip(y_diff, y_test)]
	
	def get_fault_tolerance_rate(self):
		return self.fault_tolerance_rate
