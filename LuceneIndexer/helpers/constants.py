#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This file features many constants that can be exported in order to be present throughout the python application
"""

import os

import lucene
from org.apache.lucene.analysis.core import WhitespaceAnalyzer


INDEX_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../paper_index')
ANALYZER = WhitespaceAnalyzer
