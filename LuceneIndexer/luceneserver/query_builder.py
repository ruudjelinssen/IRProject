#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This file contains the class necessary for parsing and building Apache Lucene queries based
on user free text input.

This class is mainly about using simple heuristics that we define ourselves to parse the query string
that the user specified into various components. We do this in order to show the power of Apache Lucene
and the different search techniques and models that can be present.

We pragmatically construct a query by using many of the inbuilt query classes that Apache Lucene has to offer.
"""

import lucene

from org.apache.lucene.search import BooleanQuery, BooleanClause, MatchAllDocsQuery
from org.apache.lucene.document import IntPoint


class QueryBuilder(object):

    def __init__(self, query_string):
        """
        Construct the class based on a user input query string

        :param query_string:
        """

        self.query_string = query_string

        # The Boolean query class is the one that encompasses all other queries

        self.query = BooleanQuery.Builder()

    def build_query(self):
        """
        Perform a step by step query building process

        :return:
        """

        self.__check_blank()
        self.__check_year_range()

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

            range_query = IntPoint.newRangeQuery('year', year_array[0], year_array[0])
            self.query.add(range_query, BooleanClause.Occur.MUST)
        elif len(year_array) == 2:

            range_query = IntPoint.newRangeQuery('year', year_array[0], year_array[1])
            self.query.add(range_query, BooleanClause.Occur.MUST)
