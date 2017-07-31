# Author: Zhe Zhang <zhan0915@huskers.unl.edu>

# This file is to parse job snapshots from OSG to Job object that contains meta info for a job at this particular snapshot.
# This file is imported to JobLifeCycle.py to generate life cycles for jobs.

#!/usr/bin/python

import sys
import operator

def extract_host(name):
	split_list = name.split('@')
	host = split_list[-1].strip()
	return host

class Job:

	def __init__(self,desktop_time,activity,time_current,host_set,state,site,resource,entry,daemon_start,to_retire,to_die,job_id):
		self.desktop_time = desktop_time
		self.activity = activity
		self.state = state
		self.time_current = time_current
		self.host_set = host_set
		self.site = site
		self.resource = resource
		self.entry = entry
		self.daemon_start = daemon_start
		self.to_retire = to_retire
		self.to_die = to_die
		self.job_id = job_id

	def dump(self):
		print "desktop_time : ",self.desktop_time
		print "activity : ",self.activity
		print "state : ",self.state
		print "time_current : ",self.time_current
		print "host_set : ",self.host_set
		print "site : ",self.site
		print "resource : ",self.resource
		print "entry : ",self.entry
		print "daemon_start : ",self.daemon_start
		print "to_retire : ",self.to_retire
		print "to_die : ",self.to_die
		print "job_id : ",self.job_id

class Item:

	def __init__(self,activity,time_current,name,state,site,resource,entry,daemon_start,job_start,to_retire,to_die,job_id):
		self.activity = activity
		self.time_current = time_current
		self.name = name
		self.state = state
		self.site = site
		self.resource = resource
		self.entry = entry
		self.daemon_start = daemon_start
		self.job_start = job_start
		self.to_retire = to_retire
		self.to_die = to_die
		self.job_id = job_id

	def dump(self):
		print "activity : ",self.activity
		print "state : ",self.state
		print "time_current : ",self.time_current
		print "name : ",self.name
		print "site : ",self.site
		print "resource : ",self.resource
		print "entry : ",self.entry
		print "daemon_start : ",self.daemon_start
		print "to_retire : ",self.to_retire
		print "to_die : ",self.to_die
		print "job_id : ",self.job_id

class SnapShot:

	def __init__(self,desktop_time,job_dict):
		self.desktop_time = desktop_time
		self.job_dict = job_dict
		self.job_num = len(job_dict)

	def extract_job_ids(self):
		return self.job_dict.keys()

	def dump(self):
		print "desktop_time : ",self.desktop_time
		print "job_num : ",self.job_num
		for key in self.job_dict:
			self.job_dict[key].dump()

class JobFactory:
	def __init__(self):
		self.job_cnt = 0

	def make_job(self,desktop_time,items):
		""" type 1. need to collect job statistics"""
		activity_dict = {"Idle":0,"Benchmarking":0,"Busy":0,"Suspended":0,"Retiring":0,"Vacating":0,"Killing":0}
		state_dict = {"Owner":0,"Unclaimed":0,"Matched":0,"Claimed":0,"Preempting":0,"Backfill":0,"Drained":0}
		host_set = set()
		"""type 2. need to verify if all items have the same attribute"""
		resource = "NONE"
		site = "NONE"
		entry = "NONE"
		job_id = -1
		time_current = -1
		"""type 3. need to find min or max among all items"""
		daemon_start = -1
		to_retire = -1
		to_die = -1

		for item in items:
			"""process type 1"""
			activity_dict[item.activity] += 1
			state_dict[item.state] += 1
			host_set.add(extract_host(item.name))

			if item.resource == "PSC_Bridges" and item.job_id:
				print type(item.job_id)
				item.dump()
			"""process type 2"""
			if job_id < 0:
				job_id = item.job_id
#			else:
#				if item.job_id != job_id:
#					print "Wrong job_id"
			if time_current < 0:
				time_current = item.time_current
#			else:
#				if item.time_current != time_current:
#					print "Wrong time_current",item.time_current,time_current
			if resource == "NONE":
				resource = item.resource
#			else:
#				if item.resource != resource:
#					print "Wrong resource","item: ",item.job_id,item.resource,"self: ",job_id,resource
			if site == "NONE":
				site = item.site
#			else:
#				if item.site != site:
#					print "Wrong site",item.site,site
			if entry == "NONE":
				entry = item.entry
#			else:
#				if item.entry != entry:
#					print "Wrong entry",item.entry,entry

			"""process type 3"""
			if daemon_start < 0:
				daemon_start = item.daemon_start
			else:
				daemon_start = min(daemon_start,item.daemon_start)
			if to_retire < 0:
				to_retire = item.to_retire
			else:
				to_retire = max(to_retire,item.to_retire)
			if to_die < 0:
				to_die = item.to_die
			else:
				to_die = max(to_die,item.to_die)

		activity = max(activity_dict.iteritems(), key=operator.itemgetter(1))[0]
		state =  max(state_dict.iteritems(), key=operator.itemgetter(1))[0]
		job = Job(desktop_time,activity,time_current,host_set,state,site,resource,entry,daemon_start,to_retire,to_die,job_id)

		self.job_cnt += 1
		return job

"""Parser is the class to parse the snapshots collected from OSG to job dictionary, it should take a line from snapshot as the input and call line_parser(line) and it should return a dictionary that job_id is the key and other job attributes are values. The following is an example of a line from OSG snapshot.

example:

TIME# 2017-05-09 23:49:58.993579# [[ Activity = "Busy"; MyCurrentTime = 1494373722; DaemonStartTime = 1494309813; GLIDEIN_Site = "Cinvestav"; MyType = "Machine"; Name = "glidein_1218_16492840@nodo89"; TotalJobRunTime = 63770; State = "Claimed"; GLIDEIN_Entry_Name = "CMS_T3_MX_Cinvestav_proton_work"; GLIDEIN_ToRetire = 1494362818; TargetType = "Job"; GLIDEIN_ToDie = 1494391618; GLIDEIN_ResourceName = "cinvestav"; GLIDEIN_SITEWMS_JobId = "292633.proton" ], [ Activity = "Busy"; MyCurrentTime = 1494373747; DaemonStartTime = 1494332189; GLIDEIN_Site = "Cinvestav"; MyType = "Machine"; Name = "glidein_1343_28602396@nodo89"; TotalJobRunTime = 33275; State = "Claimed"; GLIDEIN_Entry_Name = "CMS_T3_MX_Cinvestav_proton_work"; GLIDEIN_ToRetire = 1494385146; TargetType = "Job"; GLIDEIN_ToDie = 1494413946; GLIDEIN_ResourceName = "cinvestav"; GLIDEIN_SITEWMS_JobId = "292780.proton" ]]

"""
class Parser:

	def __init__(self):
		self.job_factory = JobFactory()

	"""Parsing a line where the substring between two '#' is desktop time this snapshot was taken and the rest of the line inputs to _item_parser() function.

	time_strip : 2017-05-09 23:49:58.993579
	substr     : [[ Activity = "Busy"; MyCurrentTime = 1494373722; DaemonStartTime = 1494309813; GLIDEIN_Site = "Cinvestav"; MyType = "Machine"; 
			Name = "glidein_1218_16492840@nodo89"; TotalJobRunTime = 63770; State = "Claimed"; GLIDEIN_Entry_Name = "CMS_T3_MX_Cinvestav_proton_work"; 
			GLIDEIN_ToRetire = 1494362818; TargetType = "Job"; GLIDEIN_ToDie = 1494391618; GLIDEIN_ResourceName = "cinvestav"; GLIDEIN_SITEWMS_JobId = "292633.proton" ], 
			[ Activity = "Busy"; MyCurrentTime = 1494373747; DaemonStartTime = 1494332189; GLIDEIN_Site = "Cinvestav"; MyType = "Machine"; 
			Name = "glidein_1343_28602396@nodo89"; TotalJobRunTime = 33275; State = "Claimed"; GLIDEIN_Entry_Name = "CMS_T3_MX_Cinvestav_proton_work"; 
			GLIDEIN_ToRetire = 1494385146; TargetType = "Job"; GLIDEIN_ToDie = 1494413946; GLIDEIN_ResourceName = "cinvestav"; GLIDEIN_SITEWMS_JobId = "292780.proton" ]]
	"""
	def _line_parser(self,line):
		start_time = line.index("#")
		end_time = line.rfind("#")
		time = line[start_time+2:end_time]
		body = line[end_time+1:]
		start_list = body.index("[")
		end_list = body.rfind("]")
		substr = body[start_list+1:end_list]
		time_strip = time.strip()
		job_dict = self._item_parser(time_strip, substr)
		snap_shot = SnapShot(time_strip, job_dict)
		return snap_shot

	"""Parsing a string that contains a list of jobs. We call each job in the list as an 'item'. Why don't we call it 'job'? It is because there could be some
		parallel job that runs on multiple daemons. The following example shows three items are actually the same glidein job where they run on different daemons.

	items_string : [[ Activity = "Busy"; TotalJobRunTime = 4; GLIDEIN_Site = "SU-OG"; MyType = "Machine"; Name = "glidein_2_846310905@CRUSH-SUGWG-OSG-10-5-152-79"; 
			State = "Claimed"; MyCurrentTime = 1491602071; DaemonStartTime = 1491601944; GLIDEIN_ResourceName = "SU-OG-CE"; 
			GLIDEIN_SITEWMS_JobId = "4505342.0"; GLIDEIN_Entry_Name = "Glow_US_Syracuse_condor"; GLIDEIN_ToRetire = 1491742754; TargetType = "Job"; 
			GLIDEIN_ToDie = 1491771554 ], 
			[ Activity = "Idle"; MyCurrentTime = 1491602303; GLIDEIN_Site = "SU-OG"; MyType = "Machine"; Name = "glidein_2_47225120@CRUSH-SUGWG-OSG-10-5-152-200"; 
			TargetType = "Job"; GLIDEIN_ToDie = 1491772520; GLIDEIN_ResourceName = "SU-OG-CE"; GLIDEIN_SITEWMS_JobId = "4505342.0"; State = "Unclaimed"; 
			GLIDEIN_ToRetire = 1491743720; GLIDEIN_Entry_Name = "Glow_US_Syracuse_condor"; DaemonStartTime = 1491602279 ], 
			[ Activity = "Idle"; MyCurrentTime = 1491602378; GLIDEIN_Site = "SU-OG"; MyType = "Machine"; Name = "glidein_2_14542690@CRUSH-SUGWG-OSG-10-5-153-169"; 
			TargetType = "Job"; GLIDEIN_ToDie = 1491772271; GLIDEIN_ResourceName = "SU-OG-CE"; GLIDEIN_SITEWMS_JobId = "4505342.0"; State = "Unclaimed"; 
			GLIDEIN_ToRetire = 1491743471; GLIDEIN_Entry_Name = "Glow_US_Syracuse_condor"; DaemonStartTime = 1491602350 ]]
	"""
	def _item_parser(self,desktop_time,items_string):
		"""job_items_dict stores a mapping between glidein job id to a list of items"""
		job_items_dict = {}
		item_list = items_string.split(', ')
		for i in range(len(item_list)):
			item = self._attr_parser(item_list[i])
			if item.job_id in job_items_dict:
				job_items_dict[item.job_id].append(item)
#merge(item.timeAbs,item.activity,item.state,item.name)
			else:
				job_items_dict[item.job_id] = [item]
#				job = Job(desktopTime,item.activity,item.timeAbs,item.name,item.state,item.site,item.resource,item.entry,item.daemonStart,item.toRetire,item.toDie,item.jobId)
#				job_dict[item.jobId] = job
#		for item in job_dict:
#			job_dict[item].activity = max(job_dict[item].activityDict.iteritems(), key=operator.itemgetter(1))[0]
#			job_dict[item].state =  max(job_dict[item].stateDict.iteritems(), key=operator.itemgetter(1))[0]
		job_dict = {}
		for key in job_items_dict:
			"""make_job will combine multiple items and create a job object"""
			job_items = job_items_dict[key]
			job = self.job_factory.make_job(desktop_time,job_items)
			job_dict[job.job_id] = job
		return job_dict

	"""Parsing a item_string and split it to attributes and then encapsulate them into a Item object.

	item_string : [ Activity = "Busy"; TotalJobRunTime = 4; GLIDEIN_Site = "SU-OG"; MyType = "Machine"; Name = "glidein_2_846310905@CRUSH-SUGWG-OSG-10-5-152-79"; 
                        State = "Claimed"; MyCurrentTime = 1491602071; DaemonStartTime = 1491601944; GLIDEIN_ResourceName = "SU-OG-CE"; 
                        GLIDEIN_SITEWMS_JobId = "4505342.0"; GLIDEIN_Entry_Name = "Glow_US_Syracuse_condor"; GLIDEIN_ToRetire = 1491742754; TargetType = "Job"; 
                        GLIDEIN_ToDie = 1491771554 ]
	"""
	def _attr_parser(self,item_string):
		attr_dict = {}
		start_item = item_string.index("[")
		end_item = item_string.rfind("]")
		substr = item_string[start_item+2:end_item]
		attr_list = substr.split('; ')
		for i in range(len(attr_list)):
			[key, value] = attr_list[i].split(' = ')
			key_strip = key.strip()
			attr_dict[key_strip] = value.strip()
		if "Activity" in attr_dict:
			activity = attr_dict["Activity"].strip("\"")
		else:
			activity = ""
	
		if "MyCurrentTime" in attr_dict:
			time_current = int(attr_dict["MyCurrentTime"].strip())
		else:
			time_current = 0
	
		if "Name" in attr_dict:
			name = attr_dict["Name"].strip("\"")
		else:
			name = ""
	
		if "State" in attr_dict:
			state = attr_dict["State"].strip("\"")
		else:
			state = ""
	
		if "GLIDEIN_Site" in attr_dict:
			site = attr_dict["GLIDEIN_Site"].strip("\"")
		else:
			site = ""
	
		if "GLIDEIN_ResourceName" in attr_dict:
			resource = attr_dict["GLIDEIN_ResourceName"].strip("\"")
		else:
			resource = ""
	
		if "GLIDEIN_Entry_Name" in attr_dict:
			entry = attr_dict["GLIDEIN_Entry_Name"].strip("\"")
		else:
			entry = ""
	
		if "DaemonStartTime" in attr_dict:
			daemon_start = int(attr_dict["DaemonStartTime"].strip())
		else:
			daemon_start = 0

		if "JobStart" in attr_dict:
			job_start = attr_dict["JobStart"]
		else:
			job_start = ""
	
		if "GLIDEIN_ToRetire" in attr_dict:
			to_retire = int(attr_dict["GLIDEIN_ToRetire"].strip())
		else:
			to_retire = 0
	
		if "GLIDEIN_ToDie" in attr_dict:
			to_die = int(attr_dict["GLIDEIN_ToDie"].strip())
		else:
			print resource
			to_die = 0
	
		if "GLIDEIN_SITEWMS_JobId" in attr_dict:
			job_id = attr_dict["GLIDEIN_SITEWMS_JobId"].strip("\"")
		else:
			job_id = ""
		item = Item(activity,time_current,name,state,site,resource,entry,daemon_start,job_start,to_retire,to_die,job_id)
		return item

	def read_line(self,line):
		snap_shot = self._line_parser(line)
		return snap_shot
'''
	def extractJobList(self,line):
		snapShot = line_parser(line)
		jobDict = snapShot.jobDict
		return jobDict.keys()

	def readFile(self):
		with open(self.fileName, "r") as lines:
			for line in lines:
				snapShot = lineParser(line)
				self.snapShotList.append(snapShot)
		return self.snapShotList
'''
'''
parser = Parser(sys.argv[1])
with open(sys.argv[1], "r") as lines:
	for line in lines:
		snapShot = parser.readLine(line)
		for job in snapShot.jobDict:
			print "jobId: %s , value: " % (job)

#print parser.readFile()

with open(sys.argv[1], "r") as lines:
	cnt = 0
	for line in lines:
		if cnt == 0:
			print parser.readLine(line)
		cnt = cnt + 1
'''
