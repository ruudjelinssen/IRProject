#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This file contains a simple class to make accessing papers easier since it
will now be in the form of a class, allowing operations to be performed with ease
"""

from .author import Author


class Paper:

    def __init__(self, paper_info, author_info):
        """
        Build a paper using the paper's info.

        Information must be presented as an array in the predefined manner
        as specified in this constructor

        :param paper_info:
        :param author_info:
        """
        self.id = paper_info[0]
        self.year = paper_info[1]
        self.title = paper_info[2]
        self.event_type = paper_info[3]
        self.pdf_name = paper_info[4]

        # Pre-process the abstract information already during class instantiation

        self.abstract = Paper.analyse_abstract(paper_info[5])

        self.paper_text = paper_info[6]

        self.authors = []
        self.add_author([author_info[0], author_info[1]])

    def add_author(self, author_info):
        """
        Append an author object to the authors list

        :param author_info:
        :return:
        """
        author = Author(author_info[0], author_info[1])
        self.authors.append(author)

    @staticmethod
    def analyse_abstract(abstract_text):
        """
        Analayse the abstract text and return blank if missing

        :param abstract_text:
        :return:
        """

        if abstract_text == "Abstract Missing":
            return ""
        else:
            return abstract_text
