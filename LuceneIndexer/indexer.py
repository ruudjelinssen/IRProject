#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This is a wrapper around the internal indexer class and file for top level public access
"""

from .luceneserver.indexer import Indexer
from .luceneserver.javavm import JavaVM


class IndexerWrapper:

    @staticmethod
    def index_docs(dataset_location):
        """Launch a VM and index all the documents"""

        JavaVM.init_vm()
        Indexer(dataset_location).index_docs()