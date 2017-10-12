from sklearn.neighbors import KNeighborsRegressor
import numpy as np

class CustomizedKNNRegressor:
	def __init__(self, target):
		self.target = target
		self.fault_tolerance_rate = []

	def predict(self, df_train, df_test):
		if len(df_train.index) < 5:
			regressor = KNeighborsRegressor(n_neighbors=len(df_train.index))
		else:
			regressor = KNeighborsRegressor(n_neighbors=5)
		df_train = df_train[df_train[target]!=0]
		df_test = df_test[df_test[target]!=0]
		x_train = df_train.loc[:,df_train.columns != target].values
		y_train = df_train.loc[:,df_train.columns == target].values[:,0]
		x_test = df_test.loc[:,df_test.columns != target].values
		y_test = df_test.loc[:,df_test.columns == target].values[:,0]
		regressor.fit(x_train, y_train)
		y_predict = regressor.predict(x_test)
		y_diff = y_predict - y_test
		self.fault_tolerance_rate = [abs(a*1.0/b) for a,b in zip(y_diff, y_test)]
	
	def get_fault_tolerance_rate(self):
		return self.fault_tolerance_rate
