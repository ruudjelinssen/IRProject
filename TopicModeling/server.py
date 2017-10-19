#!/usr/bin/env python
import datetime

from flask import Flask
from flask_restful import Api, Resource

from TopicModeling import models
from TopicModeling import preprocessing
from TopicModeling.routes import Paper

FLASK_PORT = 5003

app = Flask(__name__)
api = Api(app)

# Number of topics
NUM_TOPICS = 20


class TopicsServer:
    """
    Handle routing of search requests via a flask server
    """

    corpus = None
    dictionary = None
    docno_to_index = None
    lda_model = None

    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.load_models()
        self.add_routes()

    def load_models(self):
        """Load all matrices and models in memory."""
        self.corpus, self.dictionary, self.docno_to_index = preprocessing.get_from_file_or_build()
        self.lda_model = models.get_lda_model(self.corpus, self.dictionary, NUM_TOPICS)

    def init_flask_server(self, debug_mode_enabled):
        """
        Start a flask server instance
        :param debug_mode_enabled: whether the server should support live reload and verbose logging
        :return:
        """

        self.app.run(port=FLASK_PORT, debug=debug_mode_enabled)
        print('Server Running on port {}'.format(FLASK_PORT))

    def add_routes(self):
        """
        Add our api resource routes
        :return:
        """

        args = (self.lda_model, self.corpus, self.dictionary, self.docno_to_index,)

        self.api.add_resource(Paper, '/paper/<int:id>/', resource_class_args=args)
