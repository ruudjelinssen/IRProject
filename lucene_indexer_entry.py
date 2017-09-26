#!/usr/bin/env python

import sys

import lucene
from flask import Flask
from flask_restful import Api

from LuceneIndexer.luceneserver.indexer import Indexer
from LuceneIndexer.luceneserver.routes import *

app = Flask(__name__)
api = Api(app)


@app.before_first_request
def init_vm():
    """
    Launch the Java VM before every first request when the server is (re)started
    """

    try:
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        print('Launched apache lucene virtual Java instance running at', lucene.VERSION)
    except ValueError:
        print('Java VM already running - will not launch again')


def init_flask_server(debug_mode_enabled):
    """
    Start a flask server instance
    :param debug_mode_enabled: whether the server should support live reload and verbose logging
    :return:
    """

    app.run(port=5002, debug=debug_mode_enabled)
    print('Server Running on port 5002')


# Add our api resource routes

api.add_resource(Authors, '/authors')  # Route_1
api.add_resource(Papers, '/papers')  # Route_2

# Run the application if running as a script

if __name__ == '__main__':

    valid_commands = """
    Valid commands are:
        - python lucene_indexer_entry.py index
        - python lucene_indexer_entry.py serve_live
        - python lucene_indexer_entry.py serve_development
        - python lucene_indexer_entry.py serve_indexed
    """

    command = sys.argv[1]

    if not command:

        print('You must specify a command to run.')
        print(valid_commands)

    else:
        if command == 'index':

            # Start a new VM and perform the indexing operation

            init_vm()
            indexer = Indexer().index_docs()

        elif command == 'serve_live':

            # Start a new server with debug mode turned off

            init_flask_server(False)

        elif command == 'serve_indexed':

            # Index all the documents and then launch the server

            init_vm()
            indexer = Indexer().index_docs()
            init_flask_server(False)

        elif command == 'serve_development':

            # Start a new development server that supports reload when changes in a file are made

            init_flask_server(True)

        else:

            # Output that no valid command has been found and give possible options

            print('Command not supported.')
            print(valid_commands)
