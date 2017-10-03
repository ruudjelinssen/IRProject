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

    def __init__(self):
        """
        Construct the class with some default settings
        """

        # These are the variables defining what fields remain to search

        self.has_author = False
        self.has_year = False
        self.is_blank_query = True

        # The Boolean query class is the one that encompasses all other queries

        self.boolean_query_builder = BooleanQuery.Builder()

    def build_query(self, query_params):
        """
        Set the search class properties based on the passed in parameters

        :param query_params:
        :return:
        """

        if 'author' in query_params:
            self.__build_author_information(query_params['author'])
            self.has_author = True
            self.is_blank_query = False

        if 'title' in query_params:
            self.__build_title_information(query_params['title'])
            self.is_blank_query = False

        if 'abstract' in query_params:
            self.__build_abstract_information(query_params['abstract'])
            self.is_blank_query = False

        if 'event_type' in query_params:
            self.__build_event_type_information(query_params['event_type'])
            self.is_blank_query = False

        if 'paper_text' in query_params:
            self.__build_paper_text_information(query_params['paper_text'])
            self.is_blank_query = False

        if 'year' in query_params:
            self.__check_year_range(query_params['year'])
            self.has_year = True
            self.is_blank_query = False

        if 'pdf_name' in query_params:
            self.__build_pdf_name_information(query_params['pdf_name'])
            self.is_blank_query = False

        if 'query' in query_params:
            self.__build_free_text_query(query_params['query'])

        if not query_params:
            self.__check_blank('')

        return self.boolean_query_builder.build()

    def __build_free_text_query(self, query_string):
        """
        Perform a step by step query building process based on the free text and other fields filled in

        :return:
        """

        self.__check_blank(query_string)
        self.__check_year_range(query_string)
        self.__check_author_match(query_string)
        self.__check_rest_text(query_string)

    def __build_author_information(self, author_name):

        author_name_parts = author_name.split(' ')

        for part in author_name_parts:
            fuzzy_query = FuzzyQuery(Term('author', part), 2)
            self.boolean_query_builder.add(fuzzy_query, BooleanClause.Occur.MUST)

    def __build_title_information(self, title):

        title_parts = title.split(' ')

        for part in title_parts:
            term_query = TermQuery(Term('paper_title', part))
            self.boolean_query_builder.add(term_query, BooleanClause.Occur.MUST)

    def __build_abstract_information(self, query_string):

        query_string_parts = query_string.split(' ')

        for part in query_string_parts:
            term_query = TermQuery(Term('abstract', part))
            self.boolean_query_builder.add(term_query, BooleanClause.Occur.MUST)

    def __build_event_type_information(self, query_string):

        query_string_parts = query_string.split(' ')

        for part in query_string_parts:
            term_query = TermQuery(Term('event_type', part))
            self.boolean_query_builder.add(term_query, BooleanClause.Occur.MUST)

    def __build_paper_text_information(self, query_string):

        query_string_parts = query_string.split(' ')

        for part in query_string_parts:
            term_query = TermQuery(Term('paper_text', part))
            self.boolean_query_builder.add(term_query, BooleanClause.Occur.MUST)

    def __build_year_information(self, query_string):

        query_string_parts = query_string.split(' ')

        for part in query_string_parts:
            term_query = TermQuery(Term('year', part))
            self.boolean_query_builder.add(term_query, BooleanClause.Occur.MUST)

    def __build_pdf_name_information(self, query_string):

        query_string_parts = query_string.split(' ')

        for part in query_string_parts:
            term_query = TermQuery(Term('pdf_name', part))
            self.boolean_query_builder.add(term_query, BooleanClause.Occur.MUST)

    def __check_blank(self, query_string):
        """
        If the query string is blank then do a search for everything

        :return:
        """

        if query_string == '' and self.is_blank_query is True:

            all_docs_query = MatchAllDocsQuery()
            self.boolean_query_builder.add(all_docs_query, BooleanClause.Occur.MUST)

    def __check_year_range(self, query_string):
        """
        Perform basic analysis whether query string contains numbers that would then be years

        :return:
        """

        year_array = [int(s) for s in query_string.split() if s.isdigit()]

        if len(year_array) == 1:

            self.has_year = True
            range_query = IntPoint.newRangeQuery('year', year_array[0], year_array[0])
            self.boolean_query_builder.add(range_query, BooleanClause.Occur.MUST)
        elif len(year_array) == 2:

            self.has_year = True
            range_query = IntPoint.newRangeQuery('year', year_array[0], year_array[1])
            self.boolean_query_builder.add(range_query, BooleanClause.Occur.MUST)

    def __check_author_match(self, query_string):
        """
        We check to see if an author name is present and do fuzzy matching on that author name

        :return:
        """

        if 'written by' in query_string:

            self.has_author = True

            parts = self.query_string.split('written by')
            self.query_string = parts[0].strip()
            author_name = parts[1].strip()

            self.__build_author_information(author_name)

    def __check_rest_text(self, query_string):
        """
        Check if we still have something left and search weighted in the rest of the text.

        :return:
        """

        if query_string.strip() != '':

            for word in query_string.split(' '):

                term = Term('content', word)
                self.boolean_query_builder.add(TermQuery(term), BooleanClause.Occur.MUST)
