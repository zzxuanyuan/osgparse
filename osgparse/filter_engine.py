import pandas as pd

class FilterEngine:
	def __init__(self):
		pass

	def filter_exclusive(self, input_file, output_file, label_exclusive_string):
		print "label_exclusive_string = ", label_exclusive_string
		if label_exclusive_string[0] != '[' and label_exclusive_string[-1] != ']':
			label_exclusive_list = [label_exclusive_string]
		else:
			label_exclusive_list = label_exclusive_string[1:-1].split(',')
			for label in label_exlusive_list:
				label = label.strip()
		df = pd.read_csv(input_file, header=0)
		df[~df['Class'].isin(label_exclusive_list)].to_csv(output_file)

	def filter_inclusive(self, input_file, output_file, label_inclusive_string):
		print "label_inclusive_string = ", label_inclusive_string
		if label_inclusive_string[0] != '[' and label_inclusive_string[-1] != ']':
			label_inclusive_list = [label_inclusive_string]
		else:
			label_inclusive_list = label_inclusive_string[1:-1].split(',')
			print "list = ", label_inclusive_list
			for label in label_inclusive_list:
				label = label.strip()
		df = pd.read_csv(input_file, header=0)
		df[df['Class'].isin(label_inclusive_list)].to_csv(output_file)
