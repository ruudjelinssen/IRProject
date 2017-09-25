#!/usr/bin/env python

import sys, os

# Import all lucene dependencies

# Please don't remove me! I'm important so that all the other imports in this script work as well
import lucene

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, MatchAllDocsQuery


class Search:
    """Allows retrieval of search results from the given index"""

    searcher = None
    analyzer = None
    query_string = ''

    INDEX_DIR = 'LuceneIndexer/index'

    def __init__(self, query_string):
        """Initialise prerequisites to search"""

        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        directory = SimpleFSDirectory(Paths.get(os.path.join(base_dir, self.INDEX_DIR)))
        self.searcher = IndexSearcher(DirectoryReader.open(directory))
        self.analyzer = StandardAnalyzer()
        self.query_string = query_string

    def get_results(self, result_type):
        """Get results from the index based on the given query string"""

        retrieved_files = None

        print("Searching for:", self.query_string)

        if result_type == 'authors':
            retrieved_files = self.get_authors()

        if result_type == 'papers':
            retrieved_files = self.get_papers()

        return retrieved_files

    def get_authors(self):

        retrieved_files = []

        query_string = self.query_string

        if query_string != '*:*':
            query_string = 'author:' + query_string

        query = QueryParser('authors', self.analyzer).parse(query_string)

        score_docs = self.searcher.search(query, 50).scoreDocs
        print("%s total matching documents." % len(score_docs))

        for score_doc in score_docs:
            doc = self.searcher.doc(score_doc.doc)
            retrieved_files.append(doc.get('author'))

        return retrieved_files

    def get_papers(self):

        retrieved_files = []

        query_string = self.query_string

        if query_string != '*:*':
            query_string = 'title:' + query_string

        query = QueryParser('papers', self.analyzer).parse(query_string)

        score_docs = self.searcher.search(query, 50).scoreDocs
        print("%s total matching documents." % len(score_docs))

        for score_doc in score_docs:
            doc = self.searcher.doc(score_doc.doc)

            authors = []

            for author in doc.getFields('author'):
                authors.append(author.stringValue())

            retrieved_files.append({
                'title': doc.get('title'),
                'year': doc.get('year'),
                'authors': authors,
                'event_type': doc.get('event_type'),
                'pdf_name': doc.get('pdf_name'),
                'abstract': doc.get('abstract'),
            })

        return retrieved_files
