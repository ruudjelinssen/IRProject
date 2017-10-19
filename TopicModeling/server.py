#!/usr/bin/env python
import datetime

import logging
from flask import Flask
from flask_restful import Api, Resource

from TopicModeling import models
from TopicModeling import preprocessing
from TopicModeling.routes import *

FLASK_PORT = 5003

app = Flask(__name__)
api = Api(app)

# Number of topics
NUM_TOPICS = 20
TOPICS = [
    'Topic 0',
    'Topic 1',
    'Topic 2',
    'Topic 3',
    'Topic 4',
    'Topic 5',
    'Topic 6',
    'Topic 7',
    'Topic 8',
    'Topic 9',
    'Topic 10',
    'Topic 11',
    'Topic 12',
    'Topic 13',
    'Topic 14',
    'Topic 15',
    'Topic 16',
    'Topic 17',
    'Topic 18',
    'Topic 19',
]


class TopicsServer:
    """
    Handle routing of search requests via a flask server
    """

    corpus = None
    dictionary = None
    docno_to_index = None
    lda_model = None
    paper_topic_probability_matrix = None

    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.load_models()
        self.add_routes()

    def load_models(self):
        """Load all matrices and models in memory."""
        self.corpus, self.dictionary, self.docno_to_index = preprocessing.get_from_file_or_build()
        self.lda_model = models.get_lda_model(self.corpus, self.dictionary, NUM_TOPICS)
        self.paper_topic_probability_matrix = models.get_paper_topic_probabilities_matrix(
            self.lda_model,
            self.corpus,
            self.dictionary,
            self.docno_to_index
        )

    def init_flask_server(self, debug_mode_enabled):
        """
        Start a flask server instance
        :param debug_mode_enabled: whether the server should support live reload and verbose logging
        :return:
        """

        self.app.run(port=FLASK_PORT, debug=debug_mode_enabled)
        logging.info('Server Running on port {}'.format(FLASK_PORT))

    def add_routes(self):
        """
        Add our api resource routes
        :return:
        """
        self._add_resource(Paper, '/paper/<int:id>/')
        self._add_resource(SearchTopic, '/topic')
        self._add_resource(Topic, '/topic/<int:id>/')

    def _add_resource(self, resource, url):
        args = (
            self.lda_model,
            self.corpus,
            self.dictionary,
            self.docno_to_index,
            TOPICS,
            self.paper_topic_probability_matrix
        )

        self.api.add_resource(resource, url, resource_class_args=args)

