#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This is the main file that allows the NIPS paper collection to be searched and information to be retrieved.

Most importantly, this file - GETS RESULTS.
"""

import sys, os
from ..helpers import constants
from .query_builder import QueryBuilder

# Please don't remove me! I'm important so that all the other imports in this script work as well
import lucene

from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader, Term
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, Sort, SortField, SortedNumericSortField
from org.apache.lucene.search.highlight import SimpleHTMLFormatter, Highlighter, QueryScorer, TokenSources, SimpleFragmenter


class Search:

    index_reader = None
    searcher = None
    analyzer = None

    def __init__(self, query_params):
        """
        Initialise prerequisites to search

        :param query_params:
        """

        self.query_params = query_params

        # Create a new searcher  based on the already existing index

        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        store_dir = SimpleFSDirectory(Paths.get(os.path.join(base_dir, constants.INDEX_DIR)))
        self.index_reader = DirectoryReader.open(store_dir)
        self.searcher = IndexSearcher(self.index_reader)
        self.analyzer = constants.ANALYZER()

    def get_results(self, result_type):
        """
        Get results from the index based on the given query string

        :param result_type:
        :return:
        """

        print("Searching...")

        if result_type == 'papers':
            return self.__get_papers()
        else:
            print('Result type is not supported.')
            return []

    def __get_papers(self):
        """
        Build a list of papers after performing a search on papers
        :return:
        """

        result = {}
        retrieved_files = []

        qb = QueryBuilder(self.query_params)
        query = qb.build_query()
        print(query)

        if 'order' in self.query_params:

            if self.query_params['order'] == 'year':
                sort = Sort(SortedNumericSortField('year', SortField.Type.INT, True))
                hits = self.searcher.search(query, 10, sort)

            else:
                hits = self.searcher.search(query, 10)
        else:
            hits = self.searcher.search(query, 10)

        score_docs = hits.scoreDocs
        print("%s total matching documents." % len(score_docs))

        html_formatter = SimpleHTMLFormatter()
        scorer = QueryScorer(query)
        highlighter = Highlighter(html_formatter, scorer)
        fragmenter = SimpleFragmenter(50)
        highlighter.setTextFragmenter(fragmenter)

        for score_doc in score_docs:

            doc_id = score_doc.doc
            doc = self.searcher.doc(doc_id)

            full_text = doc.get('content')

            term_vectors = self.index_reader.getTermVectors(doc_id)
            token_stream = TokenSources.getTermVectorTokenStreamOrNull('content', term_vectors, -1)
            fragment = highlighter.getBestFragments(token_stream, full_text, 3, '...')

            authors = []

            for author in doc.getFields('author'):
                authors.append(author.stringValue())

            doc_result = {
                'title': doc.get('paper_title'),
                'year': doc.get('year_store'),
                'authors': authors,
                'event_type': doc.get('event_type'),
                'pdf_name': doc.get('pdf_name'),
                'abstract': doc.get('abstract'),
                'highlight': fragment,
            }

            if type(score_doc.score) == 'float':
                    doc_result['score'] = score_doc.score

            retrieved_files.append(doc_result)

        result['meta'] = {
            'total': hits.totalHits
        }
        result['results'] = retrieved_files

        return result
