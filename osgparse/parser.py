# Author: Zhe Zhang <zhan0915@huskers.unl.edu>

# This file is to parse job snapshots from OSG to Job object that contains meta info for a job at this particular snapshot.
# This file is imported to JobLifeCycle.py to generate life cycles for jobs.

#!/usr/bin/python

import sys
import osgparse.constants

def print_dict(dictionary):
	result = ""
	cnt = 0
	for key, value in sorted(dictionary.iteritems()):
		cnt += 1
		if cnt == len(dictionary):
			result += "['" + key + "'" + ":" + str(value) + "]"
		else:
			result += "['" + key + "'" + ":" + str(value) + "], "
	print result

def extract_host(name):
	split_list = name.split('@')
	host = split_list[-1].strip()
	return host

class Job:

	def __init__(self,desktop_time,activity_dict,time_current,host_set,name_set,state_dict,site,resource,entry,daemon_start,to_retire,to_die,job_id):
		self.desktop_time = desktop_time
		self.activity_dict = activity_dict
		self.state_dict = state_dict
		self.time_current = time_current
		self.host_set = host_set
		self.name_set = name_set
		self.site = site
		self.resource = resource
		self.entry = entry
		self.daemon_start = daemon_start
		self.to_retire = to_retire
		self.to_die = to_die
		self.job_id = job_id

	def dump(self):
		print "desktop_time : ",self.desktop_time
		print "activity_dict : ",print_dict(self.activity_dict)
		print "state_dict : ",print_dict(self.state_dict)
		print "time_current : ",self.time_current
		print "host_set : ",self.host_set
		print "name_set : ",self.name_set
		print "site : ",self.site
		print "resource : ",self.resource
		print "entry : ",self.entry
		print "daemon_start : ",self.daemon_start
		print "to_retire : ",self.to_retire
		print "to_die : ",self.to_die
		print "job_id : ",self.job_id

	def sorted_dump(self):
		print "desktop_time : ",self.desktop_time
		print "activity_dict : ",print_dict(self.activity_dict)
		print "state_dict : ",print_dict(self.state_dict)
		print "time_current : ",self.time_current
		print "host_set : ",sorted(self.host_set)
		print "name_set : ",sorted(self.name_set)
		print "site : ",sorted(self.site)
		print "resource : ",sorted(self.resource)
		print "entry : ",sorted(self.entry)
		print "daemon_start : ",self.daemon_start
		print "to_retire : ",self.to_retire
		print "to_die : ",self.to_die
		print "job_id : ",self.job_id

class Item:

	def __init__(self,activity,time_current,name,state,site,resource,entry,daemon_start,to_retire,to_die,job_id):
		self.activity = activity
		self.time_current = time_current
		self.name = name
		self.state = state
		self.site = site
		self.resource = resource
		self.entry = entry
		self.daemon_start = daemon_start
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
		self.job_num_resource_dict = self._categorize_by_resource(job_dict)
		assert sum(self.job_num_resource_dict.values()) == self.job_num, "resource job sum is not equal to total job number"

	def _categorize_by_resource(self, job_dict):
		job_num_resource_dict = dict()
		for job in job_dict:
			if len(job_dict[job].resource) < 1:
				print "Error: No Resource in Job"
			else:
				# convert resource set to string that splits each resource by "|"
				cnt = 0
				for r in job_dict[job].resource:
					if cnt == 0:
						resource = r
						cnt += 1
					else:
						resource += "|" + r
						cnt += 1
			if resource not in job_num_resource_dict:
				job_num_resource_dict[resource] = 1
			else:
				job_num_resource_dict[resource] += 1
		return job_num_resource_dict

	def extract_job_ids(self):
		return self.job_dict.keys()

	def dump(self):
		print "desktop_time : ",self.desktop_time
		print "job_num : ",self.job_num
		for key in self.job_dict:
			self.job_dict[key].dump()

	def sorted_dump(self):
		print "desktop_time : ",self.desktop_time
		print "job_num : ",self.job_num
		for key in sorted(self.job_dict):
			self.job_dict[key].sorted_dump()

class JobFactory:
	def __init__(self):
		self.job_cnt = 0

	def make_job(self,desktop_time,items):
		# type 1. need to collect job statistics
		activity_dict = {"Idle":0,"Benchmarking":0,"Busy":0,"Suspended":0,"Retiring":0,"Vacating":0,"Killing":0}
		state_dict = {"Owner":0,"Unclaimed":0,"Matched":0,"Claimed":0,"Preempting":0,"Backfill":0,"Drained":0}
		host_set = set()
		name_set = set()
		# type 2. need to verify if all items have the same attribute
		resource = set()
		site = set()
		entry = set()
		job_id = None
		# type 3. need to find min or max among all items
		daemon_start = None
		time_current = None # different items have different MyCurrentTime
		to_retire = None
		to_die = None

		for item in items:
			# process type 1
			activity_dict[item.activity] += 1
			state_dict[item.state] += 1
			host_set.add(extract_host(item.name))
			# add one more attribute name_set, because two different daemons could have same host name but different name and daemon_start.
			# for example, JobId: 1319029, DaemonStart: 1494503417, Name: glidein_1234567890@host1.sandhills.edu disapears at the first half minute of the minute of 100;
			#              JobId: 1319029, DaemonStart: 1494567848, Name: glidein_0987654321@host1.sandhills.edu reappears at the second half minute of the minute of 100;
			# but due to snapshot lag period we can't detect the preemption unless to verify the name_set.
			# host_set for this example should be set([host1.sandhills,edu]), but name_set should be set([glidein_1234567890@host1.sandhills.edu,glidein_0987654321@host1.sandhills.edu])
			name_set.add(item.name)

			# process type 2
			if job_id == None:
				job_id = item.job_id
				if item.job_id == None:
					raise ValueError("job_id == None")
			else:
				if item.job_id != job_id:
					raise ValueError("Wrong job_id")
			if resource == False:
				if item.resource == None:
					raise ValueError("resource == None")
				else:
					resource.add(item.resource)
			else:
				if item.resource not in resource:
					resource.add(item.resource)
					if osgparse.constants.DEBUG > 1:
						print "Add new resource : ",item.resource
					else:
						pass	
			if site == False:
				if item.site == None:
					raise ValueError("site == None")
				else:
					site.add(item.site)
			else:
				if item.site not in site:
					site.add(item.site)
					if osgparse.constants.DEBUG > 1:
						print "Add new site : ",item.site
					else:
						pass	
			if entry == False:
				if item.entry == None:
					raise ValueError("entry == None")
				else:
					entry.add(item.entry)
			else:
				if item.entry not in entry:
					entry.add(item.entry)
					if osgparse.constants.DEBUG > 1:
						print "Add new entry : ",item.entry
					else:
						pass	

			# process type 3
			if daemon_start == None:
				daemon_start = item.daemon_start
				if item.daemon_start == None:
					raise ValueError("daemon_start == None")
			else:
				if item.daemon_start != None:
					# daemon_start time should be the minimum among a parallel job and that job's start_time is the very first snapshot's daemon_start
					daemon_start = min(daemon_start,item.daemon_start)
				else:
					raise ValueError("Wrong daemon_start")
			if time_current == None:
				time_current = item.time_current
				if item.time_current == None:
					raise ValueError("time_current == None")
			else:
				if item.time_current != None:
					# time_current time should be the maximum among a parallel job and that job's end_time is the very last snapshot's time_current
					time_current = max(time_current,item.time_current)
				else:
					raise ValueError("Wrong time_current")
			if to_retire == None:
				to_retire = item.to_retire
				if item.to_retire == None:
					pass
					#raise ValueError("to_retire == None")
			else:
				if item.to_retire != None:
					to_retire = max(to_retire,item.to_retire)
				else:
					raise ValueError("Wrong to_retire")
			if to_die == None:
				to_die = item.to_die
				if item.to_die == None:
					pass
					#raise ValueError("to_die == None")
			else:
				if item.to_die != None:
					to_die = max(to_die,item.to_die)
				else:
					raise ValueError("Wrong to_die")

#		activity = max(activity_dict.iteritems(), key=operator.itemgetter(1))[0]
#		state =  max(state_dict.iteritems(), key=operator.itemgetter(1))[0]
		job = Job(desktop_time,activity_dict,time_current,host_set,name_set,state_dict,site,resource,entry,daemon_start,to_retire,to_die,job_id)
		self.job_cnt += 1
		return job

class Parser:
	"""Parser is the class to parse the snapshots collected from OSG to job dictionary, it should take a line from snapshot as the 
	input and call line_parser(line) and it should return a dictionary that job_id is the key and other job attributes are values. 
	The following example of a line from OSG snapshot:

	TIME# 2017-05-09 23:49:58.993579# [[ Activity = "Busy"; MyCurrentTime = 1494373722; DaemonStartTime = 1494309813; GLIDEIN_Site = "Cinvestav"; 
	MyType = "Machine"; Name = "glidein_1218_16492840@nodo89"; TotalJobRunTime = 63770; State = "Claimed"; GLIDEIN_Entry_Name = "CMS_T3_MX_Cinvestav_proton_work"; 
	GLIDEIN_ToRetire = 1494362818; TargetType = "Job"; GLIDEIN_ToDie = 1494391618; GLIDEIN_ResourceName = "cinvestav"; GLIDEIN_SITEWMS_JobId = "292633.proton" ], 
	[ Activity = "Busy"; MyCurrentTime = 1494373747; DaemonStartTime = 1494332189; GLIDEIN_Site = "Cinvestav"; MyType = "Machine"; 
	Name = "glidein_1343_28602396@nodo89"; TotalJobRunTime = 33275; State = "Claimed"; GLIDEIN_Entry_Name = "CMS_T3_MX_Cinvestav_proton_work"; 
	GLIDEIN_ToRetire = 1494385146; TargetType = "Job"; GLIDEIN_ToDie = 1494413946; GLIDEIN_ResourceName = "cinvestav"; GLIDEIN_SITEWMS_JobId = "292780.proton" ]]
	"""
	def __init__(self):
		self.job_factory = JobFactory()

	def _handle_missing_job_id(self,item):
		"""So far, I only encountered three cases that job_id attribute is missing:
		case 1. missing attributes(4): {GLIDEIN_Entry_Name,GLIDEIN_ToRetire,GLIDEIN_ToDie,GLIDEIN_SITEWMS_JobId}
			existing attributes:
						activity :  Idle
						state :  Unclaimed
						time_current :  1494373789
						name :  slot1@compute-1.isi.edu
						site :  ISI
						resource :  ISI
						entry :  None
						daemon_start :  1494373701
						to_retire :  None
						to_die :  None
						job_id :  None

		case 2. missing attributes(5): {Site,GLIDEIN_Entry_Name,GLIDEIN_ToRetire,GLIDEIN_ToDie,GLIDEIN_SITEWMS_JobId}
			existing attributes:
						activity :  Busy
						state :  Claimed
						time_current :  1494373620
						name :  slot1@l042.pvt.bridges.psc.edu
						site :  None
						resource :  PSC_Bridges
						entry :  None
						daemon_start :  1494362806
						to_retire :  None
						to_die :  None
						job_id :  None

		case 3. missing attributes(6): {Site,GLIDEIN_ResourceName,GLIDEIN_Entry_Name,GLIDEIN_ToRetire,GLIDEIN_ToDie,GLIDEIN_SITEWMS_JobId}
			existing attributes:
						activity :  Idle
						state :  Unclaimed
						time_current :  1494373727
						name :  slot1@xd-login.opensciencegrid.org
						site :  None
						resource :  None
						entry :  None
						daemon_start :  1493133381
						to_retire :  None
						to_die :  None
						job_id :  None

		"""
		if item.resource == None:
			# case 3
			item.site = "xd-login.opensciencegrid.org"
			item.resource = "xd-login.opensciencegrid.org"
			item.entry = "xd-login.opensciencegrid.org"
			item.to_retire = None
			item.to_die = None
			item.job_id = "xd-login.opensciencegrid.org"
		elif item.site == None:
			# case 2
			item.site = "PSC_Bridges"
			item.entry = "PSC_Bridges"
			item.to_retire = None
			item.to_die = None
			item.job_id = "PSC_Bridges"
		elif item.entry == None and item.to_retire == None and item.to_die == None and item.job_id == None:
			# case 1
			item.entry = "ISI"
			item.to_retire = None
			item.to_die = None
			item.job_id = "ISI"
		else:
			try:
				raise ValueError
			except:
				print "Have not see this case before"
		return item

	def _line_parser(self,line):
		"""Parsing a line where the substring between two '#' is desktop time this snapshot was taken and the rest of the line inputs to _item_parser() function.

		time_strip : 2017-05-09 23:49:58.993579
		substr     : [[ Activity = "Busy"; MyCurrentTime = 1494373722; DaemonStartTime = 1494309813; GLIDEIN_Site = "Cinvestav"; MyType = "Machine"; 
				Name = "glidein_1218_16492840@nodo89"; TotalJobRunTime = 63770; State = "Claimed"; GLIDEIN_Entry_Name = "CMS_T3_MX_Cinvestav_proton_work"; 
				GLIDEIN_ToRetire = 1494362818; TargetType = "Job"; GLIDEIN_ToDie = 1494391618; GLIDEIN_ResourceName = "cinvestav"; GLIDEIN_SITEWMS_JobId = "292633.proton" ], 
				[ Activity = "Busy"; MyCurrentTime = 1494373747; DaemonStartTime = 1494332189; GLIDEIN_Site = "Cinvestav"; MyType = "Machine"; 
				Name = "glidein_1343_28602396@nodo89"; TotalJobRunTime = 33275; State = "Claimed"; GLIDEIN_Entry_Name = "CMS_T3_MX_Cinvestav_proton_work"; 
				GLIDEIN_ToRetire = 1494385146; TargetType = "Job"; GLIDEIN_ToDie = 1494413946; GLIDEIN_ResourceName = "cinvestav"; GLIDEIN_SITEWMS_JobId = "292780.proton" ]]
		"""
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

	def _item_parser(self,desktop_time,items_string):
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

		# job_items_dict stores a mapping between glidein job id to a list of items
		job_items_dict = {}
		item_list = items_string.split(', ')
		job_dict = dict()
		for i in range(len(item_list)):
			item = self._attr_parser(item_list[i])
			if item == None:
				return job_dict
			if item.job_id == None:
				item = self._handle_missing_job_id(item)
#				item.dump()
			if item.job_id in job_items_dict:
				job_items_dict[item.job_id].append(item)
			else:
				job_items_dict[item.job_id] = [item]
		for key in job_items_dict:
			# make_job will combine multiple items and create a job object
			job_items = job_items_dict[key]
			job = self.job_factory.make_job(desktop_time,job_items)
			job_dict[job.job_id] = job
		return job_dict

	def _attr_parser(self,item_string):
		"""Parsing a item_string and split it to attributes and then encapsulate them into a Item object.

		item_string : [ Activity = "Busy"; TotalJobRunTime = 4; GLIDEIN_Site = "SU-OG"; MyType = "Machine"; Name = "glidein_2_846310905@CRUSH-SUGWG-OSG-10-5-152-79"; 
				State = "Claimed"; MyCurrentTime = 1491602071; DaemonStartTime = 1491601944; GLIDEIN_ResourceName = "SU-OG-CE"; 
				GLIDEIN_SITEWMS_JobId = "4505342.0"; GLIDEIN_Entry_Name = "Glow_US_Syracuse_condor"; GLIDEIN_ToRetire = 1491742754; TargetType = "Job"; 
				GLIDEIN_ToDie = 1491771554 ]

		Please node: some attributes might be missing and therefore we define missing attributes as 'None'. We must handle the case that job_id is 'None' and we do
				that in _handle_missing_job_id() method in class Item.
		"""
		if item_string == "":
			return None
		attr_dict = {}
		start_item = item_string.index("[")
		end_item = item_string.rfind("]")
		substr = item_string[start_item+2:end_item]
		attr_list = substr.split('; ')
		deficiency = False
		for i in range(len(attr_list)):
			[key, value] = attr_list[i].split(' = ')
			key_strip = key.strip()
			attr_dict[key_strip] = value.strip()
		if "Activity" in attr_dict:
			activity = attr_dict["Activity"].strip("\"")
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "Activity is not contained"
			else:
				pass
			deficiency = True
			activity = None
	
		if "MyCurrentTime" in attr_dict:
			time_current = int(attr_dict["MyCurrentTime"].strip())
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "MyCurrentTime is not contained"
			else:
				pass
			deficiency = True
			time_current = None
	
		if "Name" in attr_dict:
			name = attr_dict["Name"].strip("\"")
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "Name is not contained"
			else:
				pass
			deficiency = True
			name = None
	
		if "State" in attr_dict:
			state = attr_dict["State"].strip("\"")
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "State is not contained"
			else:
				pass
			deficiency = True
			state = None
	
		if "GLIDEIN_Site" in attr_dict:
			site = attr_dict["GLIDEIN_Site"].strip("\"")
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "Site is not contained"
			else:
				pass
			deficiency = True
			site = None
	
		if "GLIDEIN_ResourceName" in attr_dict:
			resource = attr_dict["GLIDEIN_ResourceName"].strip("\"")
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "GLIDEIN_ResourceName is not contained"
			else:
				pass
			deficiency = True
			resource = None
	
		if "GLIDEIN_Entry_Name" in attr_dict:
			entry = attr_dict["GLIDEIN_Entry_Name"].strip("\"")
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "GLIDEIN_Entry_Name is not contained"
			else:
				pass
			deficiency = True
			entry = None
	
		if "DaemonStartTime" in attr_dict:
			daemon_start = int(attr_dict["DaemonStartTime"].strip())
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "DaemonStartTime is not contained"
			else:
				pass
			deficiency = True
			daemon_start = None

		if "GLIDEIN_ToRetire" in attr_dict:
			to_retire = int(attr_dict["GLIDEIN_ToRetire"].strip())
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "GLIDEIN_ToRetire is not contained"
			else:
				pass
			deficiency = True
			to_retire = None
	
		if "GLIDEIN_ToDie" in attr_dict:
			to_die = int(attr_dict["GLIDEIN_ToDie"].strip())
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "GLIDEIN_ToDie is not contained"
			else:
				pass
			deficiency = True
			to_die = None
	
		if "GLIDEIN_SITEWMS_JobId" in attr_dict:
			job_id = attr_dict["GLIDEIN_SITEWMS_JobId"].strip("\"")
		else:
			if osgparse.constants.DEBUG > 1:
				try:
					raise ValueError
				except:
					print "GLIDEIN_SITEWMS_JobId is not contained"
			else:
				pass
			deficiency = True
			job_id = None
		item = Item(activity,time_current,name,state,site,resource,entry,daemon_start,to_retire,to_die,job_id)
		if osgparse.constants.DEBUG > 1:
			if deficiency == True:
				print item.job_id, "is missing some attribute(s)"
		return item

	def read_line(self,line):
		snap_shot = self._line_parser(line)
		return snap_shot
