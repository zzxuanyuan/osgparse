# Author: Zhe Zhang <zhan0915@huskers.unl.edu>

# This file is to collect job info from each snapshot and interpret the life cycles for each job.
# This file loads Parser.py to generate life cycles for jobs.
# This file also classify jobs into five categories: Succeeded, CleanUp, Retired, Killed, LightPreempted, HeavyPreempted.(Further analysis needs to be done including combining CleanUp and Succeeded and Combining LightPreempted and HeavyPreempted. More importantly, we need to characterize network problem that is determined as a pilot job reappears after some cycles of absence but the job start time does not change over this period).

#!/usr/bin/python

import sys
from datetime import datetime
import operator
import osgparse
import osgparse.parser
import osgparse.formatter

debug = 0
labeling = 1

class JobLifecycle:

	def __init__(self, job):
		self.start_time = job.daemon_start
		self.end_time = None
		self.desktop_start = job.desktop_time
		self.desktop_end = None
		self.host_set = job.host_set
		self.site = job.site
		self.resource = job.resource
		self.entry = job.entry
		self.to_retire = job.to_retire
		self.to_die = job.to_die
		self.job_id = job.job_id
		self.activity_dict = {"Idle":0,"Benchmarking":0,"Busy":0,"Suspended":0,"Retiring":0,"Vacating":0,"Killing":0}
		self.state_dict = {"Owner":0,"Unclaimed":0,"Matched":0,"Claimed":0,"Preempting":0,"Backfill":0,"Drained":0}
		self.activity_dict[job.activity] = 1
		self.state_dict[job.state] = 1
		if debug > 0:
			self.pair_activity_state_list = []
			tup = (job.time_current, job.activity, job.state)
			self.pair_activity_state_list.append(tup)
		else:
			self.last_activity = job.activity
			self.last_state = job.state

	def stop(self, end_time, desktop_end):
		self.end_time = end_time
		self.desktop_end = desktop_end

	def stay(self, cur_time, activity, state, host_set):
		self.start_time = min(self.start_time, cur_time)
		self.activity_dict[activity] += 1
		self.state_dict[state] += 1
		self.host_set = self.host_set.union(host_set)
		if debug > 0:
			tup = (cur_time, activity, state)
			self.pair_activity_state_list.append(tup)
		else:
			self.last_activity = activity
			self.last_state = state

	def get_last_state(self):
		if debug > 0:
			return self.pair_activity_state_list[-1][2]
		else:
			return self.last_state

	def get_last_activity(self):
		if debug > 0:
			return self.pair_activity_state_list[-1][1]
		else:
			return self.last_activity

	def dump(self):
		print "start_time : ", self.start_time
		print "end_time : ", self.end_time
		print "desktop_start : ", self.desktop_start
		print "desktop_end : ", self.desktop_end
		print "host_set : ", self.host_set
		print "site : ", self.site
		print "resource : ", self.resource
		print "entry : ", self.entry
		print "to_retire : ", self.to_retire
		print "to_die : ", self.to_die
		print "job_id : ", self.job_id
		if debug > 0:
			print "activity_dict : ", sorted(self.activity_dict)
			print "state_dict : ", sorted(self.state_dict)
		else:
			print "last_activity : ", self.last_activity
			print "last_state : ", self.last_state

class LifecycleGenerator:
	
	def __init__(self):
		self.pre_lifecycle_dict = None
		self.cur_lifecycle_dict = None
		self.pre_snapshot = None
		self.cur_snapshot = None
		self.pre_job_set = None
		self.cur_job_set = None
		self.job_freq_history_dict = dict()
		self.job_time_history_dict = dict()

	def _format_lifecycle(self,lifecycle,end_snapshot_job_num):
		lifecycle_formatter = osgparse.formatter.LifecycleFormatter(lifecycle,end_snapshot_job_num) # This is a completed job lifecycle and it should be parsed to labeling and filtering engine.

	#	if pre_filtering:
	#		lifecycle_formatter.filter_out(filter_attr_list)
		if labeling:
			lifecycle_formatter.labeling(self.job_freq_history_dict,self.job_time_history_dict)
	#	if post_filtering:
	#		lifecycle_formatter.filter_out(filter_attr_list)

		return lifecycle_formatter.formatted_lifecycle

	def generate(self,snapshot):
		if self.pre_lifecycle_dict == None and self.cur_lifecycle_dict == None and self.pre_snapshot == None and self.cur_snapshot == None and self.pre_job_set == None and self.cur_job_set == None:
			self.pre_snapshot = snapshot
			self.pre_job_set = set(self.pre_snapshot.extract_job_ids())
			self.pre_lifecycle_dict = dict()
			self.cur_job_set = set()
			self.cur_lifecycle_dict = dict()
			for beg in self.pre_job_set:
				job0 = snapshot.job_dict[beg]
				job0_lifecycle = JobLifecycle(job0)
				self.pre_lifecycle_dict[beg] = job0_lifecycle
		else:
			self.cur_snapshot = snapshot
			self.cur_job_set = set(self.cur_snapshot.extract_job_ids())
			finish_job_set = self.pre_job_set - self.cur_job_set
			begin_job_set = self.cur_job_set - self.pre_job_set
			intersect_job_set = self.pre_job_set & self.cur_job_set
			if debug > 0:
				print "finish job set : ", finish_job_set
				print "begin job set : ", begin_job_set
				print "intersect job set : ", intersect_job_set
			for inter in intersect_job_set:
				inter_lifecycle = self.pre_lifecycle_dict[inter]
				inter_job = self.cur_snapshot.job_dict[inter]
				pre_job = self.pre_snapshot.job_dict[inter]
				if inter_job.daemon_start == inter_lifecycle.start_time or inter_job.host_set.intersection(pre_job.host_set):
					inter_lifecycle.stay(inter_job.time_current,inter_job.activity,inter_job.state,inter_job.host_set)
					self.cur_lifecycle_dict[inter] = inter_lifecycle
				else:
					finish_job_set.add(inter)
					begin_job_set.add(inter)
			done_format_dict = dict()
			for fin in finish_job_set:
				fin_job = self.pre_snapshot.job_dict[fin]
				self.pre_lifecycle_dict[fin].stop(fin_job.time_current, fin_job.desktop_time)
				done_format_dict[fin] = self._format_lifecycle(self.pre_lifecycle_dict[fin], self.cur_snapshot.job_num)
				self.job_time_history_dict[fin_job.job_id] = fin_job.daemon_start
				if debug > 0:
					print_format = done_format_dict[fin]
					print_lifecycle = self.pre_lifecycle_dict[fin]
					print print_format.job_id,",",print_format.duration,",",print_format.retire_runtime,",",print_format.kill_runtime,",",print_format.end_job_num,",",print_format.desktop_time_info['startDate'],",",print_format.desktop_time_info['endDate'],",",print_format.desktop_time_info['startHour'],",",print_format.desktop_time_info['startMinute'],",",print_format.desktop_time_info['meanHour'],",",print_format.desktop_time_info['meanMinute'],",",print_format.desktop_time_info['endHour'],",",print_format.desktop_time_info['endMinute'],",",print_format.host_set,",",print_format.site,",",print_format.resource,",",print_format.entry,",",print_lifecycle.start_time,",",print_lifecycle.end_time,",",print_format.preempted_freq,",",print_format.label
				self.pre_lifecycle_dict.pop(fin)
			for beg in begin_job_set:
				job = self.cur_snapshot.job_dict[beg]
				job_lifecycle = JobLifecycle(job)
				self.cur_lifecycle_dict[beg] = job_lifecycle
			self.pre_job_set = self.cur_job_set
			self.pre_lifecycle_dict = self.cur_lifecycle_dict
			self.pre_snapshot = self.cur_snapshot
			return done_format_dict
