# Author: Zhe Zhang <zhan0915@huskers.unl.edu>

# This file generates figures of Total Jobs vs. Preempted Jobs on different grid resources.
# Input: @ARGV[1]: The csv file that contains preempted information such as days.csv(It uses day01, days02,... to separate different days' data.
#        @ARGV[2]: The csv file that contains total jobs info on different resources such as resource.csv(Add day01, day02,... to separate different days' data.

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pyplot import figure, show
import statsmodels.api as sm
import statsmodels.formula.api as smf

df = pd.read_csv(sys.argv[1], names=['JobId' , 'Duration' , 'MaxRetireTime' , 'MaxKillTime' , 'TotalJobNumber', 'DesktopStartDate', 'DesktopStartHour', 'DesktopStartMinute', 'DesktopStartHourMinute', 'DesktopStartDateMinute', 'DesktopMeanDate', 'DesktopMeanHour', 'DesktopMeanMinute', 'DesktopMeanHourMinute', 'DesktopMeanDateMinute', 'DesktopEndDate', 'DesktopEndHour' , 'DesktopEndMinute' , 'DesktopEndHourMinute', 'DesktopEndDateMinute', 'NumberOfHost', 'SiteNames' , 'ResourceNames' , 'EntryNames' , 'JobStartTime' , 'JobEndTime' , 'PreemptionFrequency' , 'Class'])
print "done"
'''
df[df['NumberOfHost']>1]['ResourceNames'].value_counts().plot(kind='bar')
plt.show()

resource_name = " "+sys.argv[2]+" "
if df['ResourceNames'][0] == resource_name:
	print "yes"
else:
	print df['ResourceNames'][0]
'''
resource_name = " "+sys.argv[2]+" "
class_name1 = " "+sys.argv[3]
class_name2 = " "+sys.argv[4]
df = df[(df['ResourceNames']==resource_name) & ((df['Class']==class_name1) | (df['Class']==class_name2))]
print df
sns.set(style='whitegrid', context='notebook')
cols = ['NumberOfHost','PreemptionFrequency','TotalJobNumber','Duration']
sns.pairplot(df[cols], size=2.5)
plt.savefig('abc.png')

'''
jobs = df[df['Class'].isin(['Succeeded'])]
for resource in resourceList:
	listCur = [0] * 1440
	r = jobs[jobs['ResourceName']==resource]
	d = r['DesktopTimeEndMinute'].value_counts()
	for index in d.index:
		listCur[index] = d[index]
	resourceDict[resource].extend(listCur)
'''
