#!/usr/bin/env python

import sys, os

# Import all lucene dependencies

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

	INDEX_DIR = "index"

	def __init__(self):
		"""Initialise prerequisites to search"""

		base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
		directory = SimpleFSDirectory(Paths.get(os.path.join(base_dir, self.INDEX_DIR)))
		self.searcher = IndexSearcher(DirectoryReader.open(directory))
		self.analyzer = StandardAnalyzer()

	def get_results(self, query_string):
		"""Get results from the index based on the given query string"""

		retrieved_files = []

		print("Searching for:", query_string)
		query = QueryParser("content", self.analyzer).parse(query_string)
		score_docs = self.searcher.search(query, 50).scoreDocs
		print("%s total matching documents." % len(score_docs))

		for score_doc in score_docs:
			doc = self.searcher.doc(score_doc.doc)
			retrieved_files.append(doc.get('content'))

		return retrieved_files
