#!/usr/bin/python

from datetime import datetime
import numpy as np
import pandas as pd
import osgparse.constants

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

class TimeseriesRecorder:

	def __init__(self,measure_date_dict):
		self.measure_date_dict = measure_date_dict
		self.job_num_dict = dict()
		self.series_size = len(measure_date_dict) * 1440
		self.job_num_dict['TotalJobNumber'] = np.array([np.nan] * self.series_size)
#		self.job_num_dict['TotalJobNumber'] = self.job_num_dict['TotalJobNumber'].astype(int)

	def record(self, snapshot):
		index = desktop_time_to_absolute_time(self.measure_date_dict, snapshot.desktop_time)
		self.job_num_dict['TotalJobNumber'][index,] = snapshot.job_num
		for job_id, job in snapshot.job_dict.iteritems():
			for resource in job.resource:
				if resource not in self.job_num_dict:
					self.job_num_dict[resource] = np.array([np.nan] * self.series_size)
#					self.job_num_dict[resource] = self.job_num_dict[resource].astype(int)
				self.job_num_dict[resource][index,] = snapshot.job_num_resource_dict[resource]

	def dump(self, outfile):
		column_names = ['TotalJobNumber']
		dump_array = self.job_num_dict['TotalJobNumber']
		for resource in sorted(self.job_num_dict):
			if resource == "TotalJobNumber":
				continue;
			else:
				column_names.append(resource)
				dump_array = np.column_stack((dump_array, self.job_num_dict[resource]))
		df = pd.DataFrame(dump_array, columns=column_names)
		df.to_csv(outfile, index=False)

