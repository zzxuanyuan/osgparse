from sklearn.ensemble import RandomForestRegressor
import numpy as np

class CustomizedRandomForestRegressor():
	def __init__(self):
		self.fault_tolerance_rate = []

	def predict(self, df_train, df_test):
		tree = RandomForestRegressor()
		df_train = df_train[df_train['Duration']!=0]
		df_test = df_test[df_test['Duration']!=0]
		x_train = df_train.loc[:,df_train.columns != 'Duration'].values
		y_train = df_train.loc[:,df_train.columns == 'Duration'].values[:,0]
		x_test = df_test.loc[:,df_test.columns != 'Duration'].values
		y_test = df_test.loc[:,df_test.columns == 'Duration'].values[:,0]
		tree.fit(x_train, y_train)
		y_predict = tree.predict(x_test)
		y_diff = y_predict - y_test
		self.fault_tolerance_rate = [abs(a*1.0/b) for a,b in zip(y_diff, y_test)]
	
	def get_fault_tolerance_rate(self):
		return self.fault_tolerance_rate
