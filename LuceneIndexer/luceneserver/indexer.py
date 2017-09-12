#!/usr/bin/env python

import sys, os, threading
from datetime import datetime

from .ticker import Ticker
from .database import DataBase

# Import all lucene related dependencies needed

import lucene

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, TextField, Field, FieldType, IntPoint
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

		document = Document()
		document.add(TextField("content", author_info, Field.Store.YES))

		self.writer.addDocument(document)

	def write_paper_to_index(self, paper):
		"""Write a single paper with author information to the index"""

		document = Document()
		document.add(IntPoint("year", paper['year']))
		document.add(TextField("title", paper['title'], Field.Store.YES))
		document.add(TextField("event_type", paper['event_type'], Field.Store.YES))
		document.add(TextField("pdf_name", paper['pdf_name'], Field.Store.YES))
		document.add(TextField("abstract", paper['abstract'], Field.Store.YES))
		document.add(TextField("paper_text", paper['paper_text'], Field.Store.YES))

		for author in paper['authors']:
			document.add(TextField('author', paper['authors'][author], Field.Store.YES))

		self.writer.addDocument(document)

	def index_all(self):
		"""Index the entire NIPS papers collection"""

		db = DataBase('dataset/database.sqlite')
		docs = db.get_all()

		for doc in docs:
			self.write_paper_to_index(docs[doc])


	def index_docs(self):
		"""Main function to start indexing the documents"""

		print('Starting Indexing Process')

		start = datetime.now()
		ticker = Ticker()
		threading.Thread(target=ticker.run).start()

		# Get all the information and write it to the index

		self.index_all()

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
