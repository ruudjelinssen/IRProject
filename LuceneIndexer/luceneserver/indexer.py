#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This file provides the functionality to index a given lists of papers, joined on their authors.
Currently, the indexing process takes over 10 minutes to perform using the standard analyzer.

The standard analyzer, as part of its job, removes predefined common stop words to make search more relevant.
"""

import os
import sys

# Please don't delete me! I'm important!
import lucene

from java.nio.file import Paths
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, TextField, Field, IntPoint, StoredField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, Term
from org.apache.lucene.store import SimpleFSDirectory


class Indexer(object):
    """Indexer class that handles creating an index from the specified input"""

    store = None
    analyzer = None
    writer = None

    dataset_location = None
    INDEX_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../index')

    def __init__(self):
        """
        Perform some initial set up
        """

        # Create an index store

        store_dir = self.__create_store_dir()
        self.store = SimpleFSDirectory(Paths.get(store_dir))

        # Create an analyser
        # We use the whitespace analyser since we want to preserve punctuation
        # This is especially relevant when taking into account all the question marks present

        self.analyzer = WhitespaceAnalyzer()

        # Create an index writer using both of the above
        # The open mode tells the writer that it should create, not append

        config = IndexWriterConfig(self.analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        self.writer = IndexWriter(self.store, config)

    def index_docs(self, docs):
        """
        Start indexing of documents
        :return:
        """

        for doc in docs:
            self.__write_paper_to_index(docs[doc])

        # Commit the result and close the writer

        self.writer.commit()
        self.writer.close()

    def __create_store_dir(self):
        """
        Create a directory for the inverted index, if it does not already exist
        :return:
        """

        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        store_dir = os.path.join(base_dir, self.INDEX_DIR)

        if not os.path.exists(store_dir):
            os.mkdir(store_dir)

        return store_dir

    def __write_paper_to_index(self, paper):
        """
        Write a single paper with author information to the index
        :param common.paper.Paper paper:
        :return:
        """

        for author in paper.authors:

            document = Document()
            document.add(IntPoint('paper_id', paper.id))
            document.add(TextField("paper_title", paper.title, Field.Store.YES))
            document.add(TextField("event_type", paper.event_type, Field.Store.YES))
            document.add(TextField("pdf_name", paper.pdf_name, Field.Store.YES))
            document.add(TextField("abstract", paper.abstract, Field.Store.YES))
            document.add(TextField("paper_text", paper.paper_text, Field.Store.YES))

            # We add the year as both an int point for easy searching
            # and as a stored field for display purposes

            document.add(IntPoint("year", paper.year))
            document.add(StoredField("year", paper.year))

            # Every author that we add to the same field simply concatenates that when searching

            document.add(TextField('author', author.name, Field.Store.YES))
            document.add(StoredField('author_id', author.id))

            self.writer.addDocument(document)
