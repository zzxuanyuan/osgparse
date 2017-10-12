import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def print_full(x):
	pd.set_option('display.max_rows', len(x))
	print(x)
	pd.reset_option('display.max_rows')

def neighbor_predict(df_train, df_test_row, cur_desktop_time):
	desktop_start_time = df_test_row['DesktopStartDateMinute']
	desktop_end_time = df_test_row['DesktopEndDateMinute']
	max_diff = 0
	neighbor_array = np.empty([0,3])
	for index, row in df_train.iterrows():
		row_start_time = row['DesktopStartDateMinute']
		row_end_time = row['DesktopEndDateMinute']
		diff = abs(row_start_time - desktop_start_time)
		row_time_tuple = [[row_start_time, row_end_time, diff]]
		if neighbor_array.shape[0] < 5:
#			print "< 5"
			neighbor_array = np.append(neighbor_array, row_time_tuple, axis=0)
			if diff > max_diff:
				max_diff = diff
		else:
#			print ">= 5, and max_diff = ", max_diff
			if diff < max_diff:
				neighbor_array[-1] = row_time_tuple[0]
				neighbor_array = neighbor_array[np.argsort(neighbor_array[:,2])]
				max_diff = neighbor_array[-1][2]
#	print "neighbor_array = ", neighbor_array
	neighbor_end_time_array = [x[1] for x in neighbor_array]
	counts = np.bincount(neighbor_end_time_array)
	predict_end_time = np.argmax(counts)
	while predict_end_time <= cur_desktop_time:
		predict_end_time += 15
#	print "predict_end_time = ", predict_end_time
	return (predict_end_time, max_diff)


class PreemptionRegressor:
	def __init__(self, attributes=['DesktopStartDateMinute','DesktopEndDateMinute'], target='DesktopEndDateMinute'):
		self.attributes = attributes
		self.target = target
		self.total_predict_job_number = 0
		self.total_miss_job_number = 0
		self.diff_dict = {'<-150':0, '-150~-135':0, '-135~-120':0, '-120~-105':0, '-105~-90':0, '-90~-75':0, '-75~-60':0, '-60~-45':0, '-45~-30':0, '-30~-15':0, '-15~0':0, '0~15':0, '15~30':0, '30~45':0, '45~60':0, '60~75':0, '75~90':0, '90~105':0, '105~120':0, '120~135':0, '135~150':0, '>150':0}

	def predict(self, df_train, df_test, cur_desktop_time):
		assert self.attributes == ['DesktopStartDateMinute','DesktopEndDateMinute']
		if len(df_train.index) < 20:
			self.total_miss_job_number += len(df_test.index)
			return -1
		df_test = df_test[df_test['DesktopEndDateMinute'] < cur_desktop_time+1000]
		print "df_train = ",
		print print_full(df_train)
		print "df_test = ",
		print print_full(df_test)

		desktop_end_date_minute_predict = np.array([])
		desktop_max_diff = np.array([])##
		for index, row in df_test.iterrows():
			pair = neighbor_predict(df_train, row, cur_desktop_time)
			desktop_end_date_minute_predict = np.append(desktop_end_date_minute_predict, pair[0])
			desktop_max_diff = np.append(desktop_max_diff, pair[1])

		diff = df_test['DesktopEndDateMinute'].values - desktop_end_date_minute_predict
		print "diff = ", diff
		print "max_diff = ", desktop_max_diff
		self.total_predict_job_number += len(diff)
		for x in diff:
			if x < -150:
				self.diff_dict['<-150'] += 1
			elif x >= -150 and x < -135:
				self.diff_dict['-150~-135'] += 1
			elif x >= -135 and x < -120:
				self.diff_dict['-135~-120'] += 1
			elif x >= -120 and x < -105:
				self.diff_dict['-120~-105'] += 1
			elif x >= -105 and x < -90:
				self.diff_dict['-105~-90'] += 1
			elif x >= -90 and x < -75:
				self.diff_dict['-90~-75'] += 1
			elif x >= -75 and x < -60:
				self.diff_dict['-75~-60'] += 1
			elif x >= -60 and x < -45:
				self.diff_dict['-60~-45'] += 1
			elif x >= -45 and x < -30:
				self.diff_dict['-45~-30'] += 1
			elif x >= -30 and x < -15:
				self.diff_dict['-30~-15'] += 1
			elif x >= -15 and x < 0:
				self.diff_dict['-15~0'] += 1
			elif x >= 0 and x < 15:
				self.diff_dict['0~15'] += 1
			elif x >= 15 and x < 30:
				self.diff_dict['15~30'] += 1
			elif x >= 30 and x < 45:
				self.diff_dict['30~45'] += 1
			elif x >= 45 and x < 60:
				self.diff_dict['45~60'] += 1
			elif x >= 60 and x < 75:
				self.diff_dict['60~75'] += 1
			elif x >= 75 and x < 90:
				self.diff_dict['75~90'] += 1
			elif x >= 90 and x < 105:
				self.diff_dict['90~105'] += 1
			elif x >= 105 and x < 120:
				self.diff_dict['105~120'] += 1
			elif x >= 120 and x < 135:
				self.diff_dict['120~135'] += 1
			elif x >= 135 and x <= 150:
				self.diff_dict['135~150'] += 1
			elif x > 150:
				self.diff_dict['>150'] += 1

	def _get_fault_tolerance_minute(self):
		print self.total_predict_job_number, self.total_miss_job_number
		return self.diff_dict

	def get_fault_tolerance(self):
		return self._get_fault_tolerance_minute()

	def plot_diff_distribution(self):
		diff_index = np.array(['<-150', '-150~-135', '-135~-120', '-120~-105', '-105~-90', '-90~-75', '-75~-60', '-60~-45', '-45~-30', '-30~-15', '-15~0', '0~15', '15~30', '30~45', '45~60', '60~75', '75~90', '90~105', '105~120', '120~135', '135~150', '>150'])
		prob_array = np.array([])
		for idx in diff_index:
			prob_array = np.append(prob_array, self.diff_dict[idx]*1.0/self.total_predict_job_number)
		plt.bar(diff_index, prob_array)
		plt.show()

	def plot_fault_tolerance_rate(self):
		abs_diff_index = np.array(['0~15', '15~30', '30~45', '45~60', '60~75', '75~90', '90~105', '105~120', '120~135', '135~150', '>150'])
		abs_diff_dict = {'0~15':self.diff_dict['-15~0']+self.diff_dict['0~15'], '15~30':self.diff_dict['-30~-15']+self.diff_dict['15~30'], '30~45':self.diff_dict['-45~-30']+self.diff_dict['30~45'], '45~60':self.diff_dict['-60~-45']+self.diff_dict['45~60'], '60~75':self.diff_dict['-75~-60']+self.diff_dict['60~75'], '75~90':self.diff_dict['-90~-75']+self.diff_dict['75~90'], '90~105':self.diff_dict['-105~-90']+self.diff_dict['90~105'], '105~120':self.diff_dict['-120~-105']+self.diff_dict['105~120'], '120~135':self.diff_dict['-135~-120']+self.diff_dict['120~135'], '135~150':self.diff_dict['-150~-135']+self.diff_dict['135~150']}
		abs_prob_array = np.array([])
		for idx in abs_diff_index:
			abs_prob_array = np.append(abs_prob_array, abs_diff_dict[idx]*1.0/self.total_predict_job_number)
		plt.plot(abs_diff_index, abs_prob_array)
		plt.show()
