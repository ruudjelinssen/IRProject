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

from org.apache.lucene.document import IntPoint
from org.apache.lucene.index import Term
from org.apache.lucene.search import BooleanQuery, BooleanClause, MatchAllDocsQuery, FuzzyQuery, TermQuery
from org.apache.lucene.search.spans import SpanMultiTermQueryWrapper, SpanNearQuery


class QueryBuilder(object):

    def __init__(self, query_params):
        """
        Construct the class with some default settings
        """

        # These are the variables defining what fields remain to search

        self.has_author = False
        self.has_year = False
        self.is_blank_query = True

        # The Boolean query class is the one that encompasses all other queries

        self.boolean_query_builder = BooleanQuery.Builder()

        self.query_params = query_params

    def build_query(self):
        """
        Set the search class properties based on the passed in parameters

        :return:
        """

        if 'author' in self.query_params:
            self.__construct_field('author', True)
            self.has_author = True

        if 'year' in self.query_params:
            self.__check_year_range(self.query_params['year'])
            self.has_year = True

        self.__construct_field('paper_title')
        self.__construct_field('abstract')
        self.__construct_field('event_type')
        self.__construct_field('paper_text')
        self.__construct_field('pdf_name')

        if 'query' in self.query_params:
            self.__build_free_text_query(self.query_params['query'])

        if not self.query_params:
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

    @staticmethod
    def construct_multi_term_span_query(field_name, term_text):
        """

        :param field_name:
        :param term_text:
        :return:
        """

        span_query_builder = SpanNearQuery.Builder(field_name, False)
        span_query_builder.setSlop(0)
        term_parts = term_text.split(' ')

        for part in term_parts:
            fuzzy_query = SpanMultiTermQueryWrapper(FuzzyQuery(Term(field_name, part), 2))
            span_query_builder.addClause(fuzzy_query)

        return span_query_builder.build()

    @staticmethod
    def construct_multi_term_query(field_name, term_text):
        """

        :param field_name:
        :param term_text:
        :return:
        """

        term_query_builder = BooleanQuery.Builder()
        term_parts = term_text.split(' ')

        for part in term_parts:
            fuzzy_query = FuzzyQuery(Term(field_name, part), 2)
            term_query_builder.add(fuzzy_query, BooleanClause.Occur.MUST)

        return term_query_builder.build()

    @staticmethod
    def construct_or_query(field_name, text, is_phrase = False):

        or_split = text.split(' or ')
        or_split = [x.strip() for x in or_split if x.strip()]

        or_query_builder = BooleanQuery.Builder()

        for or_part in or_split:

            if len(or_part.split(' ')) == 1:
                or_query_builder.add(FuzzyQuery(Term(field_name, or_split[0]), 2), BooleanClause.Occur.SHOULD)

            else:

                if is_phrase is True:
                    span_query = QueryBuilder.construct_multi_term_span_query(field_name, or_part)
                else:
                    span_query = QueryBuilder.construct_multi_term_query(field_name, or_part)

                or_query_builder.add(span_query, BooleanClause.Occur.SHOULD)

        return or_query_builder.build()

    def __construct_field(self, field_name, is_phrase = False):
        """
        Generic wrapper to be able to construct the query for a particular field

        :param field_name:
        :return:
        """

        # Don't do anything if no text is given for this field

        if field_name not in self.query_params:
            return

        text = self.query_params[field_name]
        if not text or not text.strip():
            return

        text = text.strip().lower()
        self.is_blank_query = False

        # If there is only one term for this field, add it to the builder directly

        if len(text.split(' ')) == 1:

            fuzzy_query = FuzzyQuery(Term(field_name, text), 2)
            self.boolean_query_builder.add(fuzzy_query, BooleanClause.Occur.MUST)
            return

        # Get the available AND splits

        and_split = text.split(' and ')
        and_split = [x.strip() for x in and_split if x.strip()]

        if len(and_split) > 1:

            for and_part in and_split:

                # Now we have either author names, or author names separated with ors

                or_query = QueryBuilder.construct_or_query(field_name, and_part, is_phrase)
                self.boolean_query_builder.add(or_query, BooleanClause.Occur.MUST)
            return

        # Get the available OR splits

        or_split = text.split(' or ')
        or_split = [x.strip() for x in or_split if x.strip()]

        if len(or_split) > 1:

            or_query = QueryBuilder.construct_or_query(field_name, text, is_phrase)
            self.boolean_query_builder.add(or_query, BooleanClause.Occur.MUST)
            return

        if len(text.split(' ')) > 1:

            if is_phrase is True:
                span_query = QueryBuilder.construct_multi_term_span_query(field_name, text)
            else:
                span_query = QueryBuilder.construct_multi_term_query(field_name, text)
            self.boolean_query_builder.add(span_query, BooleanClause.Occur.MUST)
            return

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

            self.__construct_field('author')

    def __check_rest_text(self, query_string):
        """
        Check if we still have something left and search weighted in the rest of the text.

        :return:
        """

        if query_string.strip() != '':

            for word in query_string.split(' '):

                term = Term('content', word)
                self.boolean_query_builder.add(TermQuery(term), BooleanClause.Occur.MUST)
