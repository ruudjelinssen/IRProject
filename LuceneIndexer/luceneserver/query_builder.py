#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This file contains the class necessary for parsing and building Apache Lucene queries based
on user free text input.

This class is mainly about using simple heuristics that we define ourselves to parse the query string
that the user specified into various components. We do this in order to show the power of Apache Lucene
and the different search techniques and models that can be present.

We pragmatically construct a query by using many of the inbuilt query classes that Apache Lucene has to offer.

We offer an exact search syntax that the user has to use. This is an alternative way of formulating queries
which still offers a rigid structure however with more of a natural feel. This is a step up from filling
in certain boxes.
"""

import lucene

from org.apache.lucene.search import BooleanQuery, BooleanClause, MatchAllDocsQuery, FuzzyQuery, TermQuery
from org.apache.lucene.document import IntPoint
from org.apache.lucene.index import Term


class QueryBuilder(object):

    def __init__(self, query_string):
        """
        Construct the class based on a user input query string

        :param query_string:
        """

        self.query_string = query_string

        # The Boolean query class is the one that encompasses all other queries

        self.query = BooleanQuery.Builder()

        # These are the variables defining what fields remain to search

        self.has_author = False
        self.has_year = False

    def build_query(self):
        """
        Perform a step by step query building process

        :return:
        """

        self.__check_blank()
        self.__check_year_range()
        self.__check_author_match()
        self.__check_rest_text()

        return self.query.build()

    def __check_blank(self):
        """
        If the query string is blank then do a search for everything

        :return:
        """

        if self.query_string == '':

            all_docs_query = MatchAllDocsQuery()
            self.query.add(all_docs_query, BooleanClause.Occur.MUST)

    def __check_year_range(self):
        """
        Perform basic analysis whether query string contains numbers that would then be years

        :return:
        """

        year_array = [int(s) for s in self.query_string.split() if s.isdigit()]

        if len(year_array) == 1:

            self.has_year = True
            range_query = IntPoint.newRangeQuery('year', year_array[0], year_array[0])
            self.query.add(range_query, BooleanClause.Occur.MUST)
        elif len(year_array) == 2:

            self.has_year = True
            range_query = IntPoint.newRangeQuery('year', year_array[0], year_array[1])
            self.query.add(range_query, BooleanClause.Occur.MUST)

    def __check_author_match(self):
        """
        We check to see if an author name is present and do fuzzy matching on that author name

        :return:
        """

        if 'written by' in self.query_string:

            self.has_author = True

            parts = self.query_string.split('written by')
            self.query_string = parts[0].strip()
            author_name = parts[1].strip()
            author_name_parts = author_name.split(' ')

            for part in author_name_parts:
                fuzzy_query = FuzzyQuery(Term('author', part), 2)
                self.query.add(fuzzy_query, BooleanClause.Occur.MUST)

    def __check_rest_text(self):
        """
        Check if we still have something left and search weighted in the rest of the text.

        :return:
        """

        if self.query_string.strip() != '':

            for word in self.query_string.split(' '):

                term = Term('content', word)
                self.query.add(TermQuery(term), BooleanClause.Occur.MUST)
