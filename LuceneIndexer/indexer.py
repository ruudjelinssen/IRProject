#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This is a wrapper around the internal indexer class and file for top level public access
"""

import threading
from datetime import datetime

from .helpers import ticker, javavm
from .luceneserver.indexer import Indexer
from common.database import DataBase


class IndexerWrapper:

    @staticmethod
    def index_docs(dataset_location):
        """
        Launch a VM and index all the documents
        :param dataset_location:
        :return:
        """

        print('Retrieving documents from database')

        docs = DataBase(dataset_location).get_all()

        print('Documents retrieved')

        javavm.JavaVM.init_vm()

        print('Starting Indexing Process')

        start = datetime.now()
        ticker_inst = ticker.Ticker()
        threading.Thread(target=ticker_inst.run).start()

        # Perform the indexing while analysing the running time

        Indexer().index_docs(docs)

        ticker_inst.tick = False
        end = datetime.now()
        print()
        print('Indexing operation took: {}'.format(end - start))
