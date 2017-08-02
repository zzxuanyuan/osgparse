# -*- coding: utf-8 -*-

import subprocess
import sys

import pytest

import osgparse


def test_cli_main_empty():
#    with pytest.raises(SystemExit):
	assert(osgparse.cli.main([])==0)

'''
def test_cli_help(capsys):
	with open('tests/test_cli/expected_cli.ini') as f:
		expected = f.read()
	out, err = capsys.readouterr()
	if(out == expected):
		print "yes!!!!!!!!!"
	print len(out),len(expected)
'''
