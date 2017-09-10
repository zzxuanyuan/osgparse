#!/usr/bin/python

from datetime import datetime
import numpy as np
import pandas as pd
import osgparse.constants
import matplotlib.pyplot as plt

"""Attribute list possiblly contains the following attributes:
'JobId' , 'Duration' , 'MaxRetireTime' , 'MaxKillTime' , 'DesktopTimeMeanHour' , 'DesktopTimeMeanMinute' , 'DesktopTimeEndHour' , 'DesktopTimeEndMinute' , 'HostName' , 'SiteName' , 'ResourceName' , 'EntryName' , 'JobEndTime' , 'JobRetireTime' , 'JobDieTime' , 'PreemptionFrequency' , 'Class'
"""

def print_dict(dictionary):
	result = ""
	cnt = 0
	for key, value in sorted(dictionary.iteritems()):
		cnt += 1
		if cnt == len(dictionary):
			result += "['" + key + "'" + ":" + str(value) + "]"
		else:
			result += "['" + key + "'" + ":" + str(value) + "], "
	return result

def max_dict(dictionary):
        return max(dictionary.iteritems(), key=operator.itemgetter(1))[0]

def desktop_time_to_absolute_time(measure_date_dict, desktop_time):
	time_list = desktop_time.split(".")
	time = time_list[0]
	time_list = time.split(" ")
	date = time_list[0]
	clock = time_list[1]
	date_list = date.split("-")
	date_rep = date_list[1] + "/" + date_list[2] + "/" + date_list[0][2:]
	converted_time = datetime.strptime(date_rep + " " + clock, "%m/%d/%y %H:%M:%S")
	date_dict = measure_date_dict[date_rep]
	return date_dict * 1440 + converted_time.hour * 60 + converted_time.minute

class Plotter:

	def __init__(self,measure_date_dict,job_instances_file,time_series_file):
		self.series_size = len(measure_date_dict) * 1440
#		self.job_instances = pd.read_csv(job_instances_file, names=['JobId' , 'Duration' , 'MaxRetireTime' , 'MaxKillTime' , 'TotalJobNumber', 'ResourceJobNumber', 'DesktopStartDate', 'DesktopStartHour', 'DesktopStartMinute', 'DesktopStartHourMinute', 'DesktopStartDateMinute', 'DesktopMeanDate', 'DesktopMeanHour', 'DesktopMeanMinute', 'DesktopMeanHourMinute', 'DesktopMeanDateMinute', 'DesktopEndDate', 'DesktopEndHour' , 'DesktopEndMinute' , 'DesktopEndHourMinute', 'DesktopEndDateMinute', 'NumberOfHost', 'SiteNames' , 'ResourceNames' , 'EntryNames' , 'JobStartTime' , 'JobEndTime' , 'PreemptionFrequency' , 'Class'])
		self.job_instances = pd.read_csv(job_instances_file, header=0)
		self.time_series = pd.read_csv(time_series_file, header=0)

	def plot_time_series(self, resource, label):
		job_num_array = np.array([np.nan] * self.series_size)
#		df = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['Class']==label) & (self.job_instances['NumberOfHost'] == 1)]
		df = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['Class']==label)]
		minutes = df['DesktopEndDateMinute'].value_counts()
		for m in minutes.index:
			job_num_array[m] = minutes[m]
		ts = self.time_series[resource]
		print np.argmax(job_num_array), max(job_num_array)
		plt.figure()
#		self.time_series['TotalJobNumber'].plot(color='green')
		ts.plot(color='red')
		plt.scatter(range(self.series_size),job_num_array,color='blue')
		plt.show()

	def plot_duration(self, resource, label):
		job_num_array = np.array([np.nan] * self.series_size)
#		df = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['Class']==label) & (self.job_instances['NumberOfHost'] == 1)]
		df = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['Class']==label)]
		minutes = df['DesktopEndDateMinute'].value_counts()
		for m in minutes.index:
			job_num_array[m] = minutes[m]
		ts = self.time_series[resource]
		listint1 = [0] * len(job_num_array)
		listint2 = [0] * len(job_num_array)
		index = 0
		distance_array = np.array([])
		for i in range(len(job_num_array)):
			if job_num_array[i] == np.nan:
				listint1[i] = 0
				listint2[i] = 0
			elif job_num_array[i] > 0:
				distance_array = np.append(distance_array,i-index)
				index = i
				listint1[i] = 1
				listint2[i] = 1
		listint1 = (listint1 - np.mean(listint1)) / (np.std(listint1) * len(listint1))
		listint2 = (listint2 - np.mean(listint2)) /  np.std(listint2)

		corr = np.correlate(listint1,listint2,mode='full')
		print corr
		print max(distance_array.tolist())
		print distance_array.tolist()
		plt.hist(distance_array.tolist(), bins=range(0,1500,20))
		plt.show()
		plt.scatter(range(len(corr)),corr)
#		plt.scatter(range(job_num_array.shape[0]), job_num_array)
		plt.show()

	def plot_time_point(self, resource, timepoint):
		plt.figure()
		timepoint = int(timepoint)
#		survivors = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['NumberOfHost'] == 1) & (self.job_instances['DesktopStartDateMinute'] <= timepoint) & (self.job_instances['DesktopEndDateMinute'] > timepoint)]
#		victims = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['NumberOfHost'] == 1) & (self.job_instances['DesktopEndDateMinute'] == timepoint)]
		survivors = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['DesktopStartDateMinute'] <= timepoint) & (self.job_instances['DesktopEndDateMinute'] > timepoint)]
		victims = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['DesktopEndDateMinute'] == timepoint)]
		print victims['JobId'].values
		print survivors['JobId'].values
		survivor_array = np.full((self.series_size, len(survivors.index)), np.nan)
		index = 0
		plot_height = 1
		for s in sorted(zip(survivors['DesktopStartDateMinute'], survivors['DesktopEndDateMinute']), key = lambda t: t[0], reverse=True):
			survivor_array[s[0]:s[1], index] = plot_height
			index += 1
			plot_height += 1
		victim_array = np.full((self.series_size, len(victims.index)), np.nan)
		index = 0
		for v in sorted(zip(victims['DesktopStartDateMinute'], victims['DesktopEndDateMinute']), key = lambda t: t[0], reverse=True):
			victim_array[v[0]:v[1], index] = plot_height
			index += 1
			plot_height += 1
		ax = pd.DataFrame(victim_array).plot(color='red', legend=False)
		pd.DataFrame(survivor_array).plot(ax=ax, color='blue',legend=False)
		if timepoint-5000 < 0:
			time_start = 0
		else:
			time_start = timepoint-5000
		time_end = timepoint + 5000
		plt.xlim(time_start, time_end)
#		plt.ylim(survivor_array.shape[1], survivor_array.shape[1]+victim_array.shape[1])
		plt.show()
