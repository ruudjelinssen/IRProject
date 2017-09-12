#!/usr/bin/env python

import sys, time


class Ticker(object):
	"""Class to write out progress indicator"""

	def __init__(self):
		"""Initialise by default we want to write labels"""
		self.tick = True

	def run(self):
		"""Print out ticks every second while it is set to true"""
		while self.tick:
			sys.stdout.write('.')
			sys.stdout.flush()
			time.sleep(1.0)
