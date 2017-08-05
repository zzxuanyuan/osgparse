#!/usr/bin/python

from datetime import datetime
import operator

"""Attribute list possiblly contains the following attributes:
'JobId' , 'Duration' , 'MaxRetireTime' , 'MaxKillTime' , 'DesktopTimeMeanHour' , 'DesktopTimeMeanMinute' , 'DesktopTimeEndHour' , 'DesktopTimeEndMinute' , 'HostName' , 'SiteName' , 'ResourceName' , 'EntryName' , 'JobEndTime' , 'JobRetireTime' , 'JobDieTime' , 'PreemptionFrequency' , 'Class'
"""

def max_dict(dictionary):
        return max(dictionary.iteritems(), key=operator.itemgetter(1))[0]

def get_desktop_time_info(desktop_start, desktop_end):
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
	time_info_dict = {}
	time_info_dict['startDate'] = date_rep_start
	time_info_dict['endDate'] = date_rep_end
	time_info_dict['startHour'] = start_time.hour
	time_info_dict['startMinute'] = start_time.hour * 60 + start_time.minute
	time_info_dict['meanHour'] = mean_time.hour
	time_info_dict['meanMinute'] = mean_time.hour * 60 + mean_time.minute
	time_info_dict['endHour'] = end_time.hour
	time_info_dict['endMinute'] = end_time.hour * 60 + end_time.minute
	return time_info_dict

class FormattedLifecycle:

	def __init__(self,lifecycle,end_snapshot_job_num):
		self.job_id = lifecycle.job_id
		self.duration = int(lifecycle.end_time) - int(lifecycle.start_time)

		# {xd-login.opensciencegrid.org, PSC_Bridges, etc. might parse None as to_retire and to_die here
		if lifecycle.to_retire is not None:
			self.retire_runtime = int(lifecycle.to_retire) - int(lifecycle.start_time)
		else:
			self.retire_runtime = None
		if lifecycle.to_die is not None:
			self.kill_runtime = int(lifecycle.to_die) - int(lifecycle.start_time)
		else:
			self.kill_runtime = None

		self.end_job_num = end_snapshot_job_num
		self.desktop_time_info = get_desktop_time_info(lifecycle.desktop_start, lifecycle.desktop_end)
		self.host_set = lifecycle.host_set
		self.site = lifecycle.site
		self.resource = lifecycle.resource
		self.entry = lifecycle.entry
		self.last_activity = lifecycle.get_last_activity()
		self.last_state = lifecycle.get_last_state()
		self.preempted_freq = 0
		self.label = None

	def dump(self):
		print "job_id : ", self.job_id
		print "duration : ", self.duration
		print "retire_runtime : ", self.retire_runtime
		print "kill_runtime : ", self.kill_runtime
		print "desktop_time_info : ", print_dict(self.desktop_time_info)
		print "host_set : ", self.host_set
		print "site : ", self.site
		print "resource : ", self.resource
		print "entry : ", self.entry
		print "last_activity : ", self.last_activity
		print "last_state : ", self.last_state
		print "preempted_freq : ", self.preempted_freq
		print "label : ", self.label

class LifecycleFormatter:

	def __init__(self,lifecycle,end_snapshot_job_num):
		self.lifecycle = lifecycle
		self.formatted_lifecycle = FormattedLifecycle(lifecycle,end_snapshot_job_num)

	def filter_out(self,attr_list):
		pass

	def labeling(self,job_freq_history_dict,job_time_history_dict):
		last_activity = self.lifecycle.get_last_activity()
		if int(self.lifecycle.end_time) < int(self.lifecycle.to_die) and int(self.lifecycle.end_time) > int(self.lifecycle.to_retire):
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
		elif self.lifecycle.job_id in job_freq_history_dict:
			if job_time_history_dict[self.lifecycle.job_id] != self.lifecycle.start_time:
				job_freq_history_dict[self.lifecycle.job_id] += 1
				self.formatted_lifecycle.preempted_freq = job_freq_history_dict[self.lifecycle.job_id]
				self.formatted_lifecycle.label = "Preempted"
			else:
				self.formatted_lifecycle.label = "NetworkIssue"
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
			self.formatted_lifecycle.label = "Benchmarking"
		else:
			self.formatted_lifecycle.label = last_activity+"Unknown"
		if self.lifecycle.job_id not in job_freq_history_dict:
			job_freq_history_dict[self.lifecycle.job_id] = 1

	def dump_internal_lifecycle(self):
		self.lifecycle.dump()
