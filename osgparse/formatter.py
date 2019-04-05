#!/usr/bin/python

from datetime import datetime
import operator
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

def get_desktop_time_info(measure_date_dict, desktop_start, desktop_end):
	start_time_list = desktop_start.split(".")
	end_time_list = desktop_end.split(".")
	time_start = start_time_list[0]
	time_end = end_time_list[0]
	time_start_list = time_start.split(" ")
	time_end_list = time_end.split(" ")
	date_start = time_start_list[0]
	date_end = time_end_list[0]
	clock_start = time_start_list[1]
	clock_end = time_end_list[1]
	date_start_list = date_start.split("-")
	date_end_list = date_end.split("-")
	date_rep_start = date_start_list[1] + "/" + date_start_list[2] + "/" + date_start_list[0][2:]
	date_rep_end = date_end_list[1] + "/" + date_end_list[2] + "/" + date_end_list[0][2:]
	start_time = datetime.strptime(date_rep_start + " " + clock_start, "%m/%d/%y %H:%M:%S")
	end_time = datetime.strptime(date_rep_end + " " + clock_end, "%m/%d/%y %H:%M:%S")
	mean_time = start_time+(end_time-start_time)/2
	date_rep_mean = mean_time.strftime("%m/%d/%y")
	time_info_dict = {}
	date_dict_start = measure_date_dict[date_rep_start]
	date_dict_mean = measure_date_dict[date_rep_mean]
	date_dict_end = measure_date_dict[date_rep_end]
	time_info_dict['StartDate'] = date_dict_start
	time_info_dict['StartHour'] = start_time.hour
	time_info_dict['StartMinute'] = start_time.minute
	time_info_dict['StartHourMinute'] = start_time.hour * 60 + start_time.minute
	time_info_dict['StartDateMinute'] = date_dict_start * 1440 + time_info_dict['StartHourMinute']
	time_info_dict['MeanDate'] = date_dict_mean
	time_info_dict['MeanHour'] = mean_time.hour
	time_info_dict['MeanMinute'] = mean_time.minute
	time_info_dict['MeanHourMinute'] = mean_time.hour * 60 + mean_time.minute
	time_info_dict['MeanDateMinute'] = date_dict_mean * 1440 + time_info_dict['MeanHourMinute']
	time_info_dict['EndDate'] = date_dict_end
	time_info_dict['EndHour'] = end_time.hour
	time_info_dict['EndMinute'] = end_time.minute
	time_info_dict['EndHourMinute'] = end_time.hour * 60 + end_time.minute
	time_info_dict['EndDateMinute'] = date_dict_end * 1440 + time_info_dict['EndHourMinute']
	return time_info_dict

class FormattedLifecycle:

	def __init__(self,measure_date_dict,lifecycle,end_snapshot_job_num,end_snapshot_job_num_resource_dict):
		self.job_id = lifecycle.job_id
		self.duration = int(lifecycle.end_time) - int(lifecycle.start_time)

		# {xd-login.opensciencegrid.org, PSC_Bridges, etc. might parse None as to_retire and to_die here. We set retire_runtime and kill_runtime as -100 if they do not exist.
		if lifecycle.to_retire is not None:
			self.retire_runtime = int(lifecycle.to_retire) - int(lifecycle.start_time)
		else:
			self.retire_runtime = -100
		if lifecycle.to_die is not None:
			self.kill_runtime = int(lifecycle.to_die) - int(lifecycle.start_time)
		else:
			self.kill_runtime = -100

		self.end_job_num = end_snapshot_job_num

		# convert resource set to string splitting by "|"
		cnt = 0
		for r in lifecycle.resource:
			if cnt == 0:
				resource = r
				cnt += 1
			else:
				resource += "|" + r
				cnt += 1

		if resource not in end_snapshot_job_num_resource_dict:
			self.end_resource_job_num = 0
		else:
			self.end_resource_job_num = end_snapshot_job_num_resource_dict[resource]

		self.desktop_time_info = get_desktop_time_info(measure_date_dict, lifecycle.desktop_start, lifecycle.desktop_end)

		self.start_time = lifecycle.start_time
		self.end_time = lifecycle.end_time
		self.host_set = lifecycle.host_set
		self.name_set = lifecycle.name_set
		self.site = lifecycle.site
		self.resource = lifecycle.resource
		self.entry = lifecycle.entry

		if osgparse.constants.DEBUG > 0:
			self.pair_activity_state_list = lifecycle.pair_activity_state_list

		self.last_activity = lifecycle.get_last_activity()
		self.last_state = lifecycle.get_last_state()
		self.preempted_freq = 0
		self.label = None

	def _print_activity_state_list(self):
		cnt = 0
		activity_state_string = ""
		for tup in self.pair_activity_state_list:
			if cnt == 0:
				activity_state_string = str(tup[1])+"."+str(tup[2])
				cnt += 1
			else:
				activity_state_string += "|"+str(tup[1])+"."+str(tup[2])
				cnt +=1
		return activity_state_string

	def dump(self):
		print "job_id : ", self.job_id
		print "duration : ", self.duration
		print "retire_runtime : ", self.retire_runtime
		print "kill_runtime : ", self.kill_runtime
		print "desktop_time_info : ", print_dict(self.desktop_time_info)
		print "host_set : ", self.host_set
		print "name_set : ", self.name_set
		print "site : ", self.site
		print "resource : ", self.resource
		print "entry : ", self.entry
		print "last_activity : ", self.last_activity
		print "last_state : ", self.last_state
		print "preempted_freq : ", self.preempted_freq
		print "label : ", self.label

	def formatted_dump(self, outfile):
		# format site, resource and entry as elements are separated by "|" symbol. For example, "Purdue_Hadoop|SU_OSG"
		string_site = None
		string_resource = None
		string_entry = None
		cnt = 0
		for site in self.site:
			if cnt == 0:
				string_site = site
				cnt += 1
			else:
				string_site = string_site + "|" + site
				cnt += 1
		cnt = 0
		for resource in self.resource:
			if cnt == 0:
				string_resource = resource
				cnt += 1
			else:
				string_resource = string_resource + "|" + resource
				cnt += 1
		cnt = 0
		for entry in self.entry:
			if cnt == 0:
				string_entry = entry
				cnt += 1
			else:
				string_entry = string_entry + "|" + entry
				cnt += 1
		# do not add whitespace between attributes because it makes life easier for pandas to read columns
		if osgparse.constants.DEBUG > 0:
			outfile.write(str(self.job_id) + "," + str(self.duration) + "," + self.label + "," + self._print_activity_state_list())
		else:
			outfile.write(str(self.job_id) + "," + str(self.duration) + "," + str(self.retire_runtime) + "," + str(self.kill_runtime) + "," + str(self.end_job_num) + "," + str(self.end_resource_job_num) + "," + str(self.desktop_time_info['StartDate']) + "," + str(self.desktop_time_info['StartHour']) + "," + str(self.desktop_time_info['StartMinute']) + "," + str(self.desktop_time_info['StartHourMinute']) + "," + str(self.desktop_time_info['StartDateMinute']) + "," + str(self.desktop_time_info['MeanDate']) + "," + str(self.desktop_time_info['MeanHour']) + "," + str(self.desktop_time_info['MeanMinute']) + "," + str(self.desktop_time_info['MeanHourMinute']) + "," + str(self.desktop_time_info['MeanDateMinute']) + "," + str(self.desktop_time_info['EndDate']) + "," + str(self.desktop_time_info['EndHour']) + "," + str(self.desktop_time_info['EndMinute']) + "," + str(self.desktop_time_info['EndHourMinute']) + "," + str(self.desktop_time_info['EndDateMinute']) + "," + str(len(self.name_set)) + "," + string_site + "," + string_resource + "," + string_entry + "," + str(self.start_time) + "," + str(self.end_time) + "," + str(self.preempted_freq) + "," + self.label + "\n")

class LifecycleFormatter:

	def __init__(self,job_freq_history_dict,job_time_history_dict,measure_date_dict):
		self.job_freq_history_dict = job_freq_history_dict
		self.job_time_history_dict = job_time_history_dict
		self.measure_date_dict = measure_date_dict
		self.lifecycle = None
		self.formatted_lifecycle = None

	def _filter_out(self,attr_list):
		pass

	def format_lifecycle(self,lifecycle,end_snapshot_job_num,end_snapshot_job_num_resource_dict):
		self.lifecycle = lifecycle
		self.formatted_lifecycle = FormattedLifecycle(self.measure_date_dict,lifecycle,end_snapshot_job_num,end_snapshot_job_num_resource_dict)
		self._filter_out([])
		self._labeling()
		return self.formatted_lifecycle

	def _labeling(self):
		last_activity = self.lifecycle.get_last_activity()
		if self.lifecycle.to_die == None or self.lifecycle.to_retire == None:
			if last_activity == "Killing" or last_activity == "Vacating":
				self.formatted_lifecycle.label = "NoDieOrRetireKilled"
			elif last_activity == "Retiring":
				self.formatted_lifecycle.label = "NoDieOrRetireRetired"
			elif last_activity == "Busy":
				self.formatted_lifecycle.label = "NoDieOrRetirePreempted"
			elif last_activity == "Idle":
				self.formatted_lifecycle.label = "NoDieOrRetireSucceeded"
			elif last_activity == "Benchmarking":
				self.formatted_lifecycle.label = "NoDieOrRetireBenchmarking"
			else:
				self.formatted_lifecycle.label = "NoDieOrRetireUnknown"
		elif int(self.lifecycle.end_time) < int(self.lifecycle.to_die) and int(self.lifecycle.end_time) > int(self.lifecycle.to_retire):
			if last_activity == "Killing" or last_activity == "Vacating":
				self.formatted_lifecycle.label = "Killed"
			elif last_activity == "Retiring":
				self.formatted_lifecycle.label = "Retired"
			else:
				self.formatted_lifecycle.label = last_activity+"Retire"
		elif int(self.lifecycle.end_time) > int(self.lifecycle.to_die):
			if last_activity == "Killing":
				self.formatted_lifecycle.label = "Killed"
			else:
				self.formatted_lifecycle.label = last_activity+"Kill"
		elif self.lifecycle.job_id in self.job_freq_history_dict:
			if self.job_time_history_dict[self.lifecycle.job_id].intersection(self.lifecycle.daemon_start_set):
				self.formatted_lifecycle.label = "NetworkIssue"
			else:
				self.job_freq_history_dict[self.lifecycle.job_id] += 1
				self.formatted_lifecycle.preempted_freq = self.job_freq_history_dict[self.lifecycle.job_id]
				self.formatted_lifecycle.label = "Preempted"
		elif max_dict(self.lifecycle.activity_dict) is "Idle":
			if last_activity == "Idle":
				self.formatted_lifecycle.label = "CleanUp"
			else:
				self.formatted_lifecycle.label = last_activity+"Stupid"
		elif max_dict(self.lifecycle.activity_dict) is "Busy":
			if last_activity == "Idle":
				self.formatted_lifecycle.label = "Succeeded"
			elif last_activity == "Busy":
				self.formatted_lifecycle.label = "Weird"
			else:
				self.formatted_lifecycle.label = last_activity+"NeedIdentify"
		elif max_dict(self.lifecycle.activity_dict) is "Benchmarking":
			self.formatted_lifecycle.label = last_activity+"Benchmarking"
		else:
			self.formatted_lifecycle.label = last_activity+"Unknown"
		if self.lifecycle.job_id not in self.job_freq_history_dict:
			self.job_freq_history_dict[self.lifecycle.job_id] = 1

	def dump(self):
		print "job_freq_history_dict : ", print_dict(self.job_freq_history_dict)
		print "job_time_history_dict : ", print_dict(self.job_time_history_dict)
