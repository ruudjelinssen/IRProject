#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
The purpose of this entry point is to provide access to the indexing and search functionality of apache lucene

You are able to choose whether to index the documents, launch a server, launch a server with debug
functionality, or index and then launch a server.

To run this file, the following syntax must be used:

python lucene_indexer_entry.py index
python lucene_indexer_entry.py serve_live
python lucene_indexer_entry.py serve_development
python lucene_indexer_entry.py serve_indexed
"""

import os, sys

from LuceneIndexer import server, indexer

valid_commands = """
Valid commands are:
    - python lucene_indexer_entry.py index
    - python lucene_indexer_entry.py serve_live
    - python lucene_indexer_entry.py serve_development
    - python lucene_indexer_entry.py serve_indexed
"""

dataset_location = 'dataset/database.sqlite'  # Edit this line to set the location of the database to be used throughout
absolute_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), dataset_location)
command = sys.argv[1]

if not command:

    print('You must specify a command to run.')
    print(valid_commands)

else:
    if command == 'index':

        # Start a new VM and perform the indexing operation
        indexer.IndexerWrapper.index_docs(absolute_path)

    elif command == 'serve_live':

        # Start a new server with debug mode turned off
        server.LuceneServer().init_flask_server(False)

    elif command == 'serve_indexed':

        # Index all the documents and then launch the server
        indexer.IndexerWrapper.index_docs(absolute_path)
        server.LuceneServer().init_flask_server(False)

    elif command == 'serve_development':

        # Start a new server with debug mode turned on (allows live reload of changed files)
        server.LuceneServer().init_flask_server(True)

    else:

        # Output that no valid command has been found and give possible options
        print('Command not supported.')
        print(valid_commands)
