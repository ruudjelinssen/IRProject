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
from org.apache.lucene.search import BooleanQuery, BooleanClause, MatchAllDocsQuery, FuzzyQuery, TermQuery, BoostQuery
from org.apache.lucene.search.spans import SpanMultiTermQueryWrapper, SpanNearQuery


class QueryBuilder(object):

    constructs = [
        'written by',
        'written about',
        'written in'
    ]

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

        if "id" in self.query_params:
            term_query = TermQuery(Term('paper_id_store', str(self.query_params['id'])))
            return term_query

        if 'author' in self.query_params:
            self.__construct_field_from_url_params('author', True)
            self.has_author = True

        if 'year' in self.query_params:
            self.__check_year_range(self.query_params['year'])
            self.has_year = True

        self.__construct_field_from_url_params('paper_title')
        self.__construct_field_from_url_params('abstract')
        self.__construct_field_from_url_params('event_type')
        self.__construct_field_from_url_params('paper_text')
        self.__construct_field_from_url_params('pdf_name')

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

        has_constructs = False

        splits = self.__find_splits(query_string)

        if self.constructs[0] in splits:
            self.__construct_field('author', splits[self.constructs[0]])
            has_constructs = True

        if self.constructs[1] in splits:

            self.__construct_field('paper_title', splits[self.constructs[1]], False, False, boost=3.0)
            self.__construct_field('paper_title', splits[self.constructs[1]], True, False, boost=4.0)
            self.__construct_field('abstract', splits[self.constructs[1]], False, False, boost=1.2)
            self.__construct_field('abstract', splits[self.constructs[1]], True, False, boost=1.4)
            self.__construct_field('paper_text', splits[self.constructs[1]], False, False, boost=1.0)
            self.__construct_field('paper_text', splits[self.constructs[1]], True, False, boost=1.0)
            has_constructs = True

        if self.constructs[2] in splits:
            self.__check_year_range(splits[self.constructs[2]])
            has_constructs = True

        if has_constructs is False:
            self.__construct_field('paper_title', query_string, False, False, boost=7.0)
            self.__construct_field('paper_title', query_string, True, False, boost=10.0)
            self.__construct_field('content', query_string, False, False)
            self.__construct_field('content', query_string, True, False)

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

    def __construct_field_from_url_params(self, field_name, is_phrase=False, must_occur=True, boost=1.0):
        """
        Wrapper to be able to construct a field using the url parameters we know of

        :param field_name:
        :param is_phrase:
        :return:
        """

        # Don't do anything if no text is given for this field

        if field_name not in self.query_params:
            return

        text = self.query_params[field_name]
        if not text or not text.strip():
            return

        self.__construct_field(field_name, text, is_phrase, must_occur, boost)

    def __construct_field(self, field_name, text, is_phrase=False, must_occur=True, boost=1.0):
        """
        Generic wrapper to be able to construct the query for a particular field

        :param field_name:
        :return:
        """

        text = text.strip().lower()
        self.is_blank_query = False

        occurrence = BooleanClause.Occur.MUST

        if must_occur is False:
            occurrence = BooleanClause.Occur.SHOULD

        # If there is only one term for this field, add it to the builder directly

        if len(text.split(' ')) == 1:

            fuzzy_query = FuzzyQuery(Term(field_name, text), 2)

            if boost != 1.0:
                fuzzy_query = BoostQuery(fuzzy_query, boost)

            self.boolean_query_builder.add(fuzzy_query, occurrence)
            return

        # Get the available AND splits

        and_split = text.split(' and ')
        and_split = [x.strip() for x in and_split if x.strip()]

        if len(and_split) > 1:

            for and_part in and_split:

                # Now we have either author names, or author names separated with ors

                or_query = QueryBuilder.construct_or_query(field_name, and_part, is_phrase)

                if boost != 1.0:
                    or_query = BoostQuery(or_query, boost)

                self.boolean_query_builder.add(or_query, occurrence)
            return

        # Get the available OR splits

        or_split = text.split(' or ')
        or_split = [x.strip() for x in or_split if x.strip()]

        if len(or_split) > 1:

            or_query = QueryBuilder.construct_or_query(field_name, text, is_phrase)

            if boost != 1.0:
                or_query = BoostQuery(or_query, boost)

            self.boolean_query_builder.add(or_query, occurrence)
            return

        if len(text.split(' ')) > 1:

            if is_phrase is True:
                span_query = QueryBuilder.construct_multi_term_span_query(field_name, text)
            else:
                span_query = QueryBuilder.construct_multi_term_query(field_name, text)

            if boost != 1.0:
                span_query = BoostQuery(span_query, boost)

            self.boolean_query_builder.add(span_query, occurrence)
            return

    def __find_splits(self, query_string):
        """
        Determine the constructs used in the query string and split these up for further processing

        :param query_string:
        :return:
        """

        query_breakdown = {}

        new_split = self.__find_split(query_string, False)

        if not new_split:

            return {}

        construct_key = new_split['construct_key']

        while new_split is not None and 'right_part' in new_split:

            new_split = self.__find_split(new_split['right_part'], True)
            query_breakdown[construct_key] = new_split['left_part']

            if 'construct_key' in new_split:
                construct_key = new_split['construct_key']

        print(query_breakdown)

        return query_breakdown

    def __find_split(self, query_string, use_left_part=False):
        """
        Find the first available construct splitting of a query string and return it

        :param query_string:
        :param use_left_part:
        :return:
        """

        smallest_index = len(query_string)
        first_construct = -1

        for list_pos, construct in enumerate(self.constructs):
            index = query_string.find(construct)

            if index < smallest_index and index > -1:
                smallest_index = index
                first_construct = list_pos

        # We now know the first construct that is used

        if first_construct == -1:

            if use_left_part is True:
                return {'left_part': query_string.strip()}
            else:
                return None

        construct_key = self.constructs[first_construct]
        right_part = query_string.split(self.constructs[first_construct])[1]

        breakdown = {
            'construct_key': construct_key,
            'right_part': right_part
        }

        if use_left_part is True:
            left_part = query_string.split(self.constructs[first_construct])[0]
            breakdown['left_part'] = left_part.strip()

        return breakdown

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
            range_query = IntPoint.newRangeQuery('year_int', year_array[0], year_array[0])
            self.boolean_query_builder.add(range_query, BooleanClause.Occur.MUST)
        elif len(year_array) == 2:

            self.has_year = True
            range_query = IntPoint.newRangeQuery('year_int', year_array[0], year_array[1])
            self.boolean_query_builder.add(range_query, BooleanClause.Occur.MUST)
