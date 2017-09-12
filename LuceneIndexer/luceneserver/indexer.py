#!/usr/bin/env python

import sys, os, lucene, threading, time
from datetime import datetime

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import \
    Document, TextField, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader, IndexReader
from org.apache.lucene.store import \
    Directory, SimpleFSDirectory

from read_csv import ReadCSV

"""
This class is loosely based on the Lucene (java implementation) demo class
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

INDEX_DIR = "../index"


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class Indexer(object):
    """Usage: python Indexer"""

    store = None
    analyzer = None
    writer = None

    def __init__(self, store_dir, analyzer):

        # If the directory to store the index doesn't exists yet, create it now

        if not os.path.exists(store_dir):
            os.mkdir(store_dir)

        self.store = SimpleFSDirectory(Paths.get(store_dir)) # Create an index store
        self.analyzer = LimitTokenCountAnalyzer(analyzer, 1048576) # Create an analyser

        # Create an index writer using both of the above

        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        self.writer = IndexWriter(self.store, config)

    def write_author_to_index(self, author_info):

        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        document = Document()
        document.add(TextField("content", author_info, Field.Store.YES))

        self.writer.addDocument(document)

    def index_docs(self):

        ticker = Ticker()
        print('commit index'),
        threading.Thread(target=ticker.run).start()

        authors = ReadCSV.get_authors()

        for author_id in authors:
            self.write_author_to_index(authors[author_id])

        self.writer.commit()
        self.writer.close()
        ticker.tick = False
        print('done')

# Launch the indexer here

if __name__ == '__main__':

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    start = datetime.now()

    try:

        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        indexer = Indexer(os.path.join(base_dir, INDEX_DIR), StandardAnalyzer())
        indexer.index_docs()
        end = datetime.now()
        print(end - start)

    except Exception as e:

        print("Failed: ", e)
        raise e