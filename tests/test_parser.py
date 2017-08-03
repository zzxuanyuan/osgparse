# -*- coding: utf-8 -*-

import os
import sys
import pytest
import filecmp

from cStringIO import StringIO

import osgparse
import osgparse.parser

def test_parser_read_single_item():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/single_item"
	tmp_path = dir_path + "/files/result_item.ini"
	
	with open(file_path, "r") as f:
		line = f.read()
	parser = osgparse.parser.Parser()
	snapshot = parser.read_line(line)
	old_stdout = sys.stdout
	sys.stdout = tmpstdout = StringIO()
	snapshot.sorted_dump()
	sys.stdout = old_stdout
	with open(tmp_path, "w") as o:
		o.write(tmpstdout.getvalue())

	expect_path = dir_path + "/files/expected_single_item.ini"
	assert filecmp.cmp(tmp_path,expect_path)
	os.remove(tmp_path)

def test_parser_read_two_diff_items():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/two_diff_items"
	tmp_path = dir_path + "/files/result_item.ini"
	
	with open(file_path, "r") as f:
		line = f.read()
	parser = osgparse.parser.Parser()
	snapshot = parser.read_line(line)
	old_stdout = sys.stdout
	sys.stdout = tmpstdout = StringIO()
	snapshot.sorted_dump()
	sys.stdout = old_stdout
	with open(tmp_path, "w") as o:
		o.write(tmpstdout.getvalue())
	expect_path = dir_path + "/files/expected_two_diff_items.ini"
	assert filecmp.cmp(tmp_path,expect_path)
	os.remove(tmp_path)


def test_parser_read_four_diff_items():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/four_diff_items"
	tmp_path = dir_path + "/files/result_item.ini"
	
	with open(file_path, "r") as f:
		line = f.read()
	parser = osgparse.parser.Parser()
	snapshot = parser.read_line(line)
	old_stdout = sys.stdout
	sys.stdout = tmpstdout = StringIO()
	snapshot.sorted_dump()
	sys.stdout = old_stdout
	with open(tmp_path, "w") as o:
		o.write(tmpstdout.getvalue())
	expect_path = dir_path + "/files/expected_four_diff_items.ini"
	assert filecmp.cmp(tmp_path,expect_path)
	os.remove(tmp_path)

def test_parser_read_three_same_items():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/three_same_items"
	tmp_path = dir_path + "/files/result_item.ini"
	
	with open(file_path, "r") as f:
		line = f.read()
	parser = osgparse.parser.Parser()
	snapshot = parser.read_line(line)
	old_stdout = sys.stdout
	sys.stdout = tmpstdout = StringIO()
	snapshot.sorted_dump()
	sys.stdout = old_stdout
	with open(tmp_path, "w") as o:
		o.write(tmpstdout.getvalue())
	expect_path = dir_path + "/files/expected_three_same_items.ini"
	assert filecmp.cmp(tmp_path,expect_path)
	os.remove(tmp_path)

def test_parser_read_two_same_items_but_diff_resources():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	file_path = dir_path + "/data/three_same_items_but_diff_resources"
	tmp_path = dir_path + "/files/result_item.ini"
	
	with open(file_path, "r") as f:
		line = f.read()
	parser = osgparse.parser.Parser()
	snapshot = parser.read_line(line)
	old_stdout = sys.stdout
	sys.stdout = tmpstdout = StringIO()
	snapshot.sorted_dump()
	sys.stdout = old_stdout
	with open(tmp_path, "w") as o:
		o.write(tmpstdout.getvalue())
	expect_path = dir_path + "/files/expected_three_same_items_but_diff_resources.ini"
	assert filecmp.cmp(tmp_path,expect_path)
	os.remove(tmp_path)
