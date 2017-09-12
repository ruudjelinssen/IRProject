#!/usr/bin/env python

import sys, os, threading
from datetime import datetime

from .read_csv import ReadCSV
from .ticker import Ticker

# Import all lucene related dependencies needed

import lucene

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, TextField, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader, IndexReader
from org.apache.lucene.store import Directory, SimpleFSDirectory


class Indexer(object):
	"""Indexer class that handles creating an index from the specified input"""

	store = None
	analyzer = None
	writer = None

	INDEX_DIR = "index"

	def __init__(self):
		"""Perform some initial set up"""

		base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
		store_dir = os.path.join(base_dir, self.INDEX_DIR)

		# If the directory to store the index doesn't exists yet, create it now

		if not os.path.exists(store_dir):
			os.mkdir(store_dir)

		self.store = SimpleFSDirectory(Paths.get(store_dir))  # Create an index store
		self.analyzer = LimitTokenCountAnalyzer(StandardAnalyzer(), 1048576)  # Create an analyser

		# Create an index writer using both of the above

		config = IndexWriterConfig(self.analyzer)
		config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
		self.writer = IndexWriter(self.store, config)

	def write_author_to_index(self, author_info):
		"""Write one author to the index"""

		t2 = FieldType()
		t2.setStored(False)
		t2.setTokenized(True)
		t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

		document = Document()
		document.add(TextField("content", author_info, Field.Store.YES))

		self.writer.addDocument(document)

	def index_docs(self):
		"""Main function to start indexing the documents"""

		print('Starting Indexing Process')

		start = datetime.now()
		ticker = Ticker()
		threading.Thread(target=ticker.run).start()

		# Get all the authors and write them to the index write

		authors = ReadCSV.get_authors()

		for author_id in authors:
			self.write_author_to_index(authors[author_id])

		# Commit the result and close the writer

		self.writer.commit()
		num_docs = self.writer.numDocs()
		self.writer.close()

		# Tear down of the function to close everything

		ticker.tick = False
		print()
		print('{} Files Indexed.'.format(num_docs))
		end = datetime.now()
		print('Indexing operation took: {}'.format(end - start))
