import csv
import numpy as np
import pandas as pd

preemption_classes = set(['Weird', 'Preempted', 'BusyStupid', 'BusyUnknown', 'BenchmarkingUnknown', 'BenchmarkingNeedIdentify',
		'BenchmarkingStupid', 'NoDieOrRetirePreempted'])
normal_classes = set(['BusyRetire', 'IdleRetire', 'CleanUp', 'RetiringKill', 'Succeeded', 'BusyKill', 'IdleKill', 'NetworkIssue', 'Benchmarking', 'Killed', 'IdleUnknown',
		'RetiringUnknown', 'RetiringNeedIdentify', 'BenchmarkingRetire', 'BenchmarkingKill', 'VacatingUnknown', 'VacatingNeedIdentify', 'Retired',
		'RetiringStupid', 'VacatingStupid', 'VacatingKill', 'NoDieOrRetireSucceeded', 'KillingNeedIdentify', 'KillingUnknown', 'NoDieOrRetireRetired',
		'KillingStupid'])

retire_classes = set(['BusyRetire', 'IdleRetire', 'RetiringUnknown', 'RetiringNeedIdentify', 'BenchmarkingRetire', 'Retired', 'RetiringStupid', 'NoDieOrRetireRetired'])
kill_classes = set(['RetiringKill', 'BusyKill', 'IdleKill', 'Killed', 'BenchmarkingKill', 'VacatingUnknown', 'VacatingNeedIdentify', 'VacatingStupid', 'VacatingKill', 'KillingNeedIdentify', 'KillingUnknown', 'KillingStupid'])
network_classes = set(['NetworkIssue'])
recycle_classes = set(['CleanUp', 'Succeeded', 'Benchmarking', 'IdleUnknown', 'NoDieOrRetireSucceeded'])

def increment0preemption(job_instances_file, output_file):
	with open(job_instances_file, 'r') as fr:
		with open(output_file, 'w') as fw:
			reader = csv.DictReader(fr)
			header = reader.fieldnames
			writer = csv.DictWriter(fw, fieldnames=header)
			writer.writeheader()
			for row in reader:
				if row['Class'] == 'Preemption' and row['PreemptionFrequency'] == '0':
					row['PreemptionFrequency'] = '1'
				writer.writerow(row)

def changelabel(job_instances_file, output_file, number_of_labels=2):
	if number_of_labels == 2:
		_to2labels(job_instances_file, output_file)
	elif number_of_labels == 5:
		_to5labels(job_instances_file, output_file)

def _to2labels(job_instances_file, output_file):
	print preemption_classes.intersection(normal_classes)
	assert len(preemption_classes.intersection(normal_classes)) == 0
	with open(job_instances_file, 'r') as fr:
		with open(output_file, 'w') as fw:
			reader = csv.DictReader(fr)
			header = reader.fieldnames
			writer = csv.DictWriter(fw, fieldnames=header)
			writer.writeheader()
			for row in reader:
				if row['Class'] in normal_classes:
					row['Class'] = 'Normal'
				elif row['Class'] in preemption_classes:
					row['Class'] = 'Preemption'
				else:
					print 'There does not exist such a class', row['Class']
				writer.writerow(row)

def _to5labels(job_instances_file, output_file):
	df = pd.read_csv(job_instances_file, header=0)
	labels = df['Class'].value_counts().index
	for l in labels:
		l = str(l)
        print len(labels)
	print labels
	label_set = set(labels)
        tmp_set = preemption_classes.union(retire_classes).union(kill_classes).union(network_classes).union(recycle_classes)
        print len(tmp_set)
        print tmp_set
	#assert label_set == preemption_classes.union(retire_classes).union(kill_classes).union(network_classes).union(recycle_classes)
	with open(job_instances_file, 'r') as fr:
		with open(output_file, 'w') as fw:
			reader = csv.DictReader(fr)
			header = reader.fieldnames
			writer = csv.DictWriter(fw, fieldnames=header)
			writer.writeheader()
			for row in reader:
				if row['Class'] in retire_classes:
					row['Class'] = 'Retire'
				elif row['Class'] in kill_classes:
					row['Class'] = 'Kill'
				elif row['Class'] in network_classes:
					row['Class'] = 'NetworkIssue'
				elif row['Class'] in recycle_classes:
					row['Class'] = 'IdleShutDown'
				elif row['Class'] in preemption_classes:
					row['Class'] = 'Preemption'
				else:
					print 'There does not exist such a class', row['Class']
				writer.writerow(row)
