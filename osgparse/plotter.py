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
		self.day_list = ["Day"+str(d) for d in range(len(measure_date_dict))]
		self.series_size = len(measure_date_dict) * 1440
#		self.job_instances = pd.read_csv(job_instances_file, names=['JobId' , 'Duration' , 'MaxRetireTime' , 'MaxKillTime' , 'TotalJobNumber', 'ResourceJobNumber', 'DesktopStartDate', 'DesktopStartHour', 'DesktopStartMinute', 'DesktopStartHourMinute', 'DesktopStartDateMinute', 'DesktopMeanDate', 'DesktopMeanHour', 'DesktopMeanMinute', 'DesktopMeanHourMinute', 'DesktopMeanDateMinute', 'DesktopEndDate', 'DesktopEndHour' , 'DesktopEndMinute' , 'DesktopEndHourMinute', 'DesktopEndDateMinute', 'NumberOfHost', 'SiteNames' , 'ResourceNames' , 'EntryNames' , 'JobStartTime' , 'JobEndTime' , 'PreemptionFrequency' , 'Class'])
		self.job_instances = pd.read_csv(job_instances_file, header=0)
		self.time_series = pd.read_csv(time_series_file, header=0)

	def _get_positions(self):
		cur_pos = 0
		position_list = range(1440/2, self.series_size, 1440)
		return position_list

	def plot_time_series(self, resource, label):
		if resource != None and label != None:
			fig = plt.figure()
			p1 = plt.subplot(1,2,1)
			job_num_array = np.array([np.nan] * self.series_size)
			df = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['Class']==label)]
			minutes = df['DesktopEndDateMinute'].value_counts()
			for m in minutes.index:
				job_num_array[m] = minutes[m]
			ts = self.time_series[resource]
			temp = job_num_array
			temp = np.nan_to_num(job_num_array)
			print np.argmax(temp), max(temp)
			print temp.shape
			print np.sort(temp)[-200:]
			print temp.argsort()[-200:][::-1]
#			print job_num_array[120959],job_num_array[41027],job_num_array[41014],job_num_array[41015],job_num_array[41016]
			ts.plot(color='red')
			ts_array = ts.values
			total_running_jobs, = plt.plot(range(self.series_size), ts_array, color='red', label='Total Running Jobs')
			preemption_jobs, = plt.plot(range(self.series_size),job_num_array,color='blue', label='Preemption Jobs')
			a1 = plt.gca()
			a1.set_xlim(xmin=0)
			a1.set_ylim(ymin=0)
			ylabel = 'Number of Job Instances'
			a1.set_ylabel(ylabel)
			a1.set_xticks(self._get_positions())
			a1.set_xticklabels(self.day_list,rotation=50,fontsize=9)
			for index, tick in enumerate(a1.xaxis.get_ticklabels()):
				if index % 5 != 0:
					tick.set_visible(False)
			plt.grid()
			p2 = plt.subplot(1,2,2)
			ts.plot(color='red')
			plt.plot(range(self.series_size),job_num_array,color='blue')
			a2 = plt.gca()
			a2.set_xlim(xmin=0)
			a2.set_xticks(self._get_positions())
			a2.set_xticklabels(self.day_list,rotation=50,fontsize=9)
			for index, tick in enumerate(a2.xaxis.get_ticklabels()):
				if index % 5 != 0:
					tick.set_visible(False)
			plt.grid()
			plt.yscale('log')
			fig.legend([total_running_jobs, preemption_jobs],['Total Running Jobs','Preemption Jobs'], ncol=2, loc='lower center', bbox_to_anchor=(0,0.9,1,1), borderaxespad=0)
			file_name = resource + '_' + label + '_timeseries'
			file_name = '/Users/zhezhang/osgparse/figures/' + file_name
			plt.savefig(file_name)
			plt.show()
		elif label == None:
			if resource == None:
				df = self.job_instances
				ts = self.time_series['TotalJobNumber']
			else:
				df = self.job_instances[self.job_instances['ResourceNames']==resource]
				ts = self.time_series[resource]
			job_total_num_array = np.array([np.nan] * self.series_size)
			job_retire_num_array = np.array([np.nan] * self.series_size)
			job_kill_num_array = np.array([np.nan] * self.series_size)
			job_preemption_num_array = np.array([np.nan] * self.series_size)
			job_networkissue_num_array = np.array([np.nan] * self.series_size)
			job_recycle_num_array = np.array([np.nan] * self.series_size)
			minutes_total = df['DesktopEndDateMinute'].value_counts()
			minutes_retire = df[df['Class']=='Retire']['DesktopEndDateMinute'].value_counts()
			minutes_kill = df[df['Class']=='Kill']['DesktopEndDateMinute'].value_counts()
			minutes_preemption = df[df['Class']=='Preemption']['DesktopEndDateMinute'].value_counts()
			minutes_networkissue = df[df['Class']=='NetworkIssue']['DesktopEndDateMinute'].value_counts()
			minutes_recycle = df[df['Class']=='Recycle']['DesktopEndDateMinute'].value_counts()

			for m in minutes_total.index:
				job_total_num_array[m] = minutes_total[m]
			for m in minutes_retire.index:
				job_retire_num_array[m] = minutes_retire[m]
			for m in minutes_kill.index:
				job_kill_num_array[m] = minutes_kill[m]
			for m in minutes_preemption.index:
				job_preemption_num_array[m] = minutes_preemption[m]
			for m in minutes_networkissue.index:
				job_networkissue_num_array[m] = minutes_networkissue[m]
			for m in minutes_recycle.index:
				job_recycle_num_array[m] = minutes_recycle[m]

			fig = plt.figure()
			p1 = plt.subplot(6,2,1)
			ts_array = ts.values
			print ts_array.shape[0], ts.shape[0]
			ts.plot(color='red', label='Total Running Jobs')
			total_running_jobs, = plt.plot(range(self.series_size), ts_array, color='red', label='Total Running Jobs')
			retire_jobs, = plt.plot(range(self.series_size),job_retire_num_array,label='Retire Jobs',color='orange')
			a1 = plt.gca()
#			a1.set_title("Different Types of Jobs vs. Total Running Jobs")
			a1.set_xlim(xmin=0)
			a1.set_ylim(ymin=0)
			a1.set_ylabel("Retire")
			a1.set_xticks(self._get_positions())
			a1.set_xticklabels([])
#			plt.legend(loc='upper right', prop={'size':10})
			plt.grid()

			p2 = plt.subplot(6,2,2)
			ts.plot(color='red', label='Total Running Jobs')
			plt.plot(range(self.series_size),job_retire_num_array,label='Retire Jobs',color='orange')
			a2 = plt.gca()
#			a2.set_title("(Log Scale)")
			a2.set_xlim(xmin=0)
			a2.set_xticks(self._get_positions())
			a2.set_xticklabels([])
#			plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
			plt.grid()
			plt.yscale('log')

			p3 = plt.subplot(6,2,3)
			ts.plot(color='red', label='Total Running Jobs')
			kill_jobs, = plt.plot(range(self.series_size),job_kill_num_array,label='Kill Jobs',color='y')
			a3 = plt.gca()
			a3.set_xlim(xmin=0)
			a3.set_ylim(ymin=0)
			a3.set_ylabel("Kill")
			a3.set_xticks(self._get_positions())
			a3.set_xticklabels([])
			plt.grid()

			p4 = plt.subplot(6,2,4)
			ts.plot(color='red', label='Total Running Jobs')
			plt.plot(range(self.series_size),job_kill_num_array,label='Kill Jobs',color='y')
			a4 = plt.gca()
			a4.set_xlim(xmin=0)
			a4.set_xticks(self._get_positions())
			a4.set_xticklabels([])
#			plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
			plt.grid()
			plt.yscale('log')

			p5 = plt.subplot(6,2,5)
			ts.plot(color='red', label='Total Running Jobs')
			preemption_jobs, = plt.plot(range(self.series_size),job_preemption_num_array,label='Preemption Jobs',color='g')
			a5 = plt.gca()
			a5.set_ylabel("Preemption")
			a5.set_xlim(xmin=0)
			a5.set_ylim(ymin=0)
			a5.set_xticks(self._get_positions())
			a5.set_xticklabels([])
			plt.grid()

			p6 = plt.subplot(6,2,6)
			ts.plot(color='red', label='Total Running Jobs')
			plt.plot(range(self.series_size),job_preemption_num_array,label='Preemption Jobs',color='g')
			a6 = plt.gca()
			a6.set_xlim(xmin=0)
			a6.set_xticks(self._get_positions())
			a6.set_xticklabels([])
			plt.grid()
			plt.yscale('log')

			p7 = plt.subplot(6,2,7)
			ts.plot(color='red', label='Total Running Jobs')
			networkissue_jobs, = plt.plot(range(self.series_size),job_networkissue_num_array,label='NetworkIssue Jobs',color='b')
			a7 = plt.gca()
			a7.set_xlim(xmin=0)
			a7.set_ylim(ymin=0)
			a7.set_ylabel("NetworkIssue")
			a7.set_xticks(self._get_positions())
			a7.set_xticklabels([])
			plt.grid()

			p8 = plt.subplot(6,2,8)
			ts.plot(color='red', label='Total Running Jobs')
			plt.plot(range(self.series_size),job_networkissue_num_array,label='NetworkIssue Jobs',color='b')
			a8 = plt.gca()
			a8.set_xlim(xmin=0)
			a8.set_xticks(self._get_positions())
			a8.set_xticklabels([])
#			plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
			plt.grid()
			plt.yscale('log')

			p9 = plt.subplot(6,2,9)
			ts.plot(color='red', label='Total Running Jobs')
			recycle_jobs, = plt.plot(range(self.series_size),job_recycle_num_array,label='Recycle Jobs',color='c')
			a9 = plt.gca()
			a9.set_xlim(xmin=0)
			a9.set_ylim(ymin=0)
			a9.set_ylabel("Recycle")
			a9.set_xticks(self._get_positions())
			a9.set_xticklabels([])
			plt.grid()

			p10 = plt.subplot(6,2,10)
			ts.plot(color='red', label='Total Running Jobs')
			plt.plot(range(self.series_size),job_recycle_num_array,label='Recycle Jobs',color='c')
			a10 = plt.gca()
			a10.set_xlim(xmin=0)
			a10.set_xticks(self._get_positions())
			a10.set_xticklabels([])
#			plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
			plt.grid()
			plt.yscale('log')

			p11 = plt.subplot(6,2,11)
			ts.plot(color='red', label='Total Running Jobs')
			total_ending_jobs, = plt.plot(range(self.series_size),job_total_num_array,label='Total Ending Jobs',color='purple')
			a11 = plt.gca()
			a11.set_xlim(xmin=0)
			a11.set_ylim(ymin=0)
			a11.set_ylabel("Total")
			a11.set_xticks(self._get_positions())
			a11.set_xticklabels(self.day_list,rotation=50,fontsize=9)
			for index, label in enumerate(a11.xaxis.get_ticklabels()):
				if index % 5 != 0:
					label.set_visible(False)
			plt.grid()

			p12 = plt.subplot(6,2,12)
			ts.plot(color='red', label='Total Running Jobs')
			plt.plot(range(self.series_size),job_total_num_array,label='Total Ending Jobs',color='purple')
			a12 = plt.gca()
			a12.set_xlim(xmin=0)
			a12.set_xticks(self._get_positions())
			a12.set_xticklabels(self.day_list,rotation=50,fontsize=9)
			for index, label in enumerate(a12.xaxis.get_ticklabels()):
				if index % 5 != 0:
					label.set_visible(False)
			plt.grid()
			plt.yscale('log')
			fig.legend([total_running_jobs, retire_jobs, kill_jobs, preemption_jobs, networkissue_jobs, recycle_jobs, total_ending_jobs],['Total Running Jobs','Retire Jobs','Kill Jobs','Preemption Jobs','NetworkIssue Jobs','Recycle Jobs','Total Ending Jobs'], ncol=7, loc='lower center', bbox_to_anchor=(0,0.9,1,1), borderaxespad=0)
			plt.show()

	def plot_preemption_distribution(self):
		df = self.job_instances
		maxval = df['PreemptionFrequency'].max()
		freq_list = list()
		total = len(df['JobId'].value_counts())
		print 'total = ',total
		preempt = df[df['Class']=='Preemption']
		print len(preempt['JobId'].value_counts())
		print len(preempt[preempt['PreemptionFrequency']>0]['JobId'].value_counts())
		for i in range(0, maxval+1):
			preempt = preempt[preempt['PreemptionFrequency'] > i]
			freq = len(preempt['JobId'].value_counts())
			prob = freq * 1.0 / total
			freq_list.append(prob)
		print freq,prob
		print freq_list
		plt.figure()
		plt.bar(range(1,len(freq_list)+1),freq_list)
#		plt.title('Distribution of Preemption Probability')
		ax = plt.gca()
		ax.set_xlabel("Preemption Occurrences of Each Job")
		ax.set_ylabel("Ratio to the Total Number of Jobs")
		ax.set_xlim(xmin=0)
		ax.set_ylim(ymin=0)
		zoomin = plt.axes([0.35,0.2,0.5,0.5])
		plt.bar([1,2,3,4,5,6,7,8,9,10], freq_list[0:10])
		bx = plt.gca()
		bx.set_xticks([1,2,3,4,5,6,7,8,9,10])
		#bx.set_xticklabels(['1', '8', '16', '32', '64', '128', '256', '512', '1024'])
		plt.title('Preemption Occurred Less than 10')
		plt.grid()
		#plt.legend(loc='upper right')
		plt.tight_layout()
		plt.savefig("preemptioncountdist.png")
		plt.show()

	def plot_job_distance(self, resource, label):
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
		print distance_array.size, len(distance_array.tolist())
		distance_array = distance_array.astype(int)
		bin_count = np.bincount(distance_array)
		print bin_count
		bin_count = bin_count.astype(float)
		bin_count_sum = sum(bin_count)
		bin_count_prob = bin_count/bin_count_sum
		cumulative = 0
		bin_count_cumu = np.array([])
		for prob in bin_count_prob:
			prob += cumulative
			bin_count_cumu = np.append(bin_count_cumu, prob)
			cumulative = prob
		bin_count_prob[bin_count_prob == 0] = np.nan
		bin_count_cumu[bin_count_cumu == 0] = np.nan
		fig = plt.figure(1)
		p1 = plt.subplot(1,2,1)
		plt.scatter(range(bin_count_prob.size), bin_count_prob)
		plt.xlabel("Preemption Distance (Minutes)")
		plt.ylabel("Probability Distribution")
		p2 = plt.subplot(1,2,2)
		plt.scatter(range(bin_count_cumu.size), bin_count_cumu)
		plt.xlabel("Preemption Distance (Minutes)")
		plt.ylabel("Cumulative Probability Distribution")
		file_name = resource + '_' + label + '_preemptiondistancedist'
		file_name = '/Users/zhezhang/osgparse/figures/' + file_name
		fig.savefig(file_name)
		plt.show()
		fig = plt.figure(2)
		p1 = plt.subplot(1,2,1)
		plt.scatter(range(bin_count_prob.size), bin_count_prob)
		plt.xlabel("Preemption Distance (Minutes)")
		plt.ylabel("Probability Distribution")
		plt.xlim(0, 60)
		p2 = plt.subplot(1,2,2)
		plt.scatter(range(bin_count_cumu.size), bin_count_cumu)
		plt.xlabel("Preemption Distance (Minutes)")
		plt.ylabel("Cumulative Probability Distribution")
		plt.xlim(0, 60)
		file_name = resource + '_' + label + '_preemptiondistancedist_1hour'
		file_name = '/Users/zhezhang/osgparse/figures/' + file_name
		fig.savefig(file_name)
		plt.show()
#		plt.scatter(range(len(corr)),corr)
#		plt.scatter(range(job_num_array.shape[0]), job_num_array)
#		plt.show()

	def plot_time_point(self, resource, timepoint):
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
#		plt.ylim(survivor_array.shape[1]-100, survivor_array.shape[1]+victim_array.shape[1])
		plt.show()

	def plot_desktop_start_end_correlation(self, resource, label):
		plt.figure()
		print self.job_instances
		df = self.job_instances[(self.job_instances['ResourceNames'] == resource) & (self.job_instances['Class'] == label)]
		print df['DesktopStartDateMinute']
		print df['DesktopEndDateMinute']
		plt.scatter(df['DesktopStartDateMinute'], df['DesktopEndDateMinute'])
		plt.xlim(40000,45000)
		plt.show()

	def plot_time_diff(self, resource, label, attr1, attr2):
		plt.figure()
		if label == None and resource == None:
			print "label is none and resource is none"
			df = self.job_instances
		elif label == None and resource != None:
			df = self.job_instances[self.job_instances['ResourceNames']==resource]
		elif label != None and resource == None:
			df = self.job_instances[self.job_instances['Class']==label]
		else:
			df = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['Class']==label)]
		diff_df = df.loc[:,[attr1,attr2]].astype(int)
		diff_df = diff_df[(diff_df[attr1] >= 0) & (diff_df[attr2] >= 0)]
		diff_abs_array = abs(diff_df[attr1].values - diff_df[attr2].values)
		diff_minute = diff_abs_array/60
		bin_count = np.bincount(diff_minute)
		bin_count = bin_count.astype(float)
		bin_count[bin_count == 0] = np.nan
		plt.scatter(range(bin_count.size), bin_count)
		plt.show()

	def plot_fault_tolerance(self, resource, label):
		plt.figure()
		if label == None and resource == None:
			print "label is none and resource is none"
			df = self.job_instances
		elif label == None and resource != None:
			df = self.job_instances[self.job_instances['ResourceNames']==resource]
		elif label != None and resource == None:
			df = self.job_instances[self.job_instances['Class']==label]
		else:
			df = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['Class']==label)]
		if label == 'Retire':
			attr = 'MaxRetireTime'
		elif label == 'Kill':
			attr = 'MaxKillTime'
		else:
			print "Not a valid attributes. Should be Retire or Kill"
		diff_df = df.loc[:,['Duration',attr]].astype(int)
		diff_df = diff_df[(diff_df['Duration'] >= 0) & (diff_df[attr] >= 0)]
		diff_attr_array = diff_df[attr].values
		diff_abs_array = abs(diff_df['Duration'].values - diff_df[attr].values)
		diff_percentage_array = diff_abs_array * 1.0 / diff_attr_array
		result_array = np.array([])
		percentage_array = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 5.0, 10.0]
		for percentage in percentage_array:
			result_array = np.append(result_array, len(diff_percentage_array[diff_percentage_array <= percentage])*1.0/len(diff_percentage_array))
		print result_array
		plt.plot(range(0,len(result_array)), result_array, label=attr)
		ax = plt.gca()
		ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13])
		ax.set_xticklabels(['1%','5%','10%','20%','30%','40%','50%','60%','70%','80%','90%','100%','500%','1000%'],rotation=40,fontsize=12)
		ax.set_ylim(0,1.1)
		plt.xlabel('Fault Tolerance Percentage',fontsize=14)
		plt.legend(loc='lower right',prop={'size':12})
		plt.tight_layout()
		plt.grid()
		plt.show()
#		fig.savefig('regression10h.png')

	def plot_max_retire_or_kill_time(self, resource, label, attr):
		plt.figure()
		if label == None and resource == None:
			print "label is none and resource is none"
			df = self.job_instances
		elif label == None and resource != None:
			df = self.job_instances[self.job_instances['ResourceNames']==resource]
		elif label != None and resource == None:
			df = self.job_instances[self.job_instances['Class']==label]
		else:
			df = self.job_instances[(self.job_instances['ResourceNames']==resource) & (self.job_instances['Class']==label)]
		max_time_df = df[attr].astype(int)
		max_time_df = max_time_df[max_time_df >= 0]
		max_time_array = max_time_df.values
		max_time_array_minute = max_time_array/60
		bin_count = np.bincount(max_time_array_minute)
		bin_count = bin_count.astype(float)
		bin_count[bin_count == 0] = np.nan
		plt.scatter(range(bin_count.size), bin_count)
		plt.show()

	def plot_job_distribution(self, attr, label):
		plt.figure()
		df = self.job_instances
		if attr == 'ResourceNames':
			name_dict = dict()
			names = df[attr].value_counts().index
			print names
			index = 0
			for name in sorted(names):
				name_dict[name] = 'C'+str(index)
				index += 1
		if label != None:
			df = df[df['Class']==label]
		value_count = df[attr].value_counts()
		value_count = value_count / len(df.index)
		if attr == 'ResourceNames':
			ax = value_count.plot(kind='bar', rot=90)
			xticklabels_old = ax.get_xticklabels()
			for key in name_dict:
				print key, name_dict[key]
			xticklabels_new = [name_dict[name.get_text()] for name in xticklabels_old]
			ax.set_xticklabels(xticklabels_new)
			plt.xlabel('Clusters')
		else:
			ax = value_count.plot(kind='bar', rot=0)
		plt.ylabel('Percentage to Total Number of Jobs')
		if attr == 'ResourceNames':
			zoomin = plt.axes([0.4,0.3,0.5,0.5])
			value_count = value_count[0:10]
			bx = value_count.plot(kind='bar', rot=60, fontsize=9)
			x10_old = bx.get_xticklabels()
			x10_new = [name_dict[name.get_text()] for name in x10_old]
			bx.set_xticklabels(x10_new)
			plt.title('Top 10')
		plt.grid()
		plt.tight_layout()
		if label == None:
			file_name = attr + '_jobdist.png'
		else:
			file_name = attr + '_' + label + '_jobdist.png'
		file_name = '/Users/zhezhang/osgparse/figures/' + file_name
		plt.savefig(file_name)
		plt.show()

	def plot_duration(self, label):
		pass
