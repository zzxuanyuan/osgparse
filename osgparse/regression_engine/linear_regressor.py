from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def print_full(x):
	pd.set_option('display.max_rows', len(x))
	print(x)
	pd.reset_option('display.max_rows')


class CustomizedLinearRegressor:
	def __init__(self, attributes=['DesktopStartDateMinute','DesktopEndDateMinute'], target='DesktopEndDateMinute'):
#		assert attributes == ['DesktopStartDateMinute','DesktopEndDateMinute']
		self.attributes = attributes
		self.target = target
		self.fault_tolerance_rate = []

	def predict(self, df_train, df_test, cur_desktop_time):
		regressor = LinearRegression()
		test_duration = df_test['Duration'].values
		df_train = df_train[['DesktopStartDateMinute','DesktopEndDateMinute']]
		print "df_train has ", len(df_train.index), " samples"
		if len(df_train.index) < 20:
			return -1
		df_test = df_test[['DesktopStartDateMinute','DesktopEndDateMinute']]
		x_train = df_train.loc[:,df_train.columns != self.target].values
		y_train = df_train.loc[:,df_train.columns == self.target].values[:,0]
		x_test = df_test.loc[:,df_test.columns != self.target].values
		y_test = df_test.loc[:,df_test.columns == self.target].values[:,0]
		print "x_train.shape and y_train.shape: "
		print x_train.shape, y_train.shape
		regressor.fit(x_train, y_train)
		y_predict = regressor.predict(x_test)
		y_diff = y_predict - y_test
#		self.fault_tolerance_rate = [abs(a*1.0/b) for a,b in zip(y_diff, y_test)]
		df = pd.DataFrame(index=range(len(y_test)),columns=['CurrentDesktopTime','DesktopStartDateMinute','DesktopEndDateMinute','PredictedEndMinute','Diff','Duration'])
		df['CurrentDesktopTime'] = np.array([cur_desktop_time]*len(y_test))
		df['DesktopStartDateMinute'] = np.array(x_test[:,0])
		df['DesktopEndDateMinute'] = np.array(y_test)
		df['PredictedEndMinute'] = np.array(y_predict)
		df['Diff'] = np.array(y_diff)
		df['Duration'] = np.array(test_duration)
#		arr = np.array([[cur_desktop_time]*len(y_test), x_test[:,0], y_test, y_predict, y_diff, test_duration])
#		np.set_printoptions(threshold=np.nan)
		print df.shape
		print "df_train : "
		print(df_train.to_string())
		print "df : "
		print(df.to_string())
#		print "sort by desktop start date time: "
#		print arr[arr[:,1].argsort()]
#		print "sort by desktop end date time: "
#		print arr[arr[:,2].argsort()]
#		for i in range(len(y_diff)):
#			print cur_desktop_time, y_test[i], y_predict[i], y_diff[i], test_duration[i]
#		plt.scatter(df_test['DesktopStartDateMinute'], df_test['DesktopEndDateMinute'])
#		plt.show()

	def get_fault_tolerance_rate(self):
		return self.fault_tolerance_rate
