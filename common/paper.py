#!/usr/bin/env python


class Paper:
	def __init__(self, paper_info, author_info):

		self.id = paper_info[0]
		self.year = paper_info[1]
		self.title = paper_info[2]
		self.event_type = paper_info[3]
		self.pdf_name = paper_info[4]
		self.abstract = paper_info[5]
		self.paper_text = paper_info[6]

		self.authors = {author_info[0]: author_info[1]}

	def add_author(self, author_info):

		self.authors[author_info[0]] = author_info[1]
