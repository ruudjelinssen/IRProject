#!/usr/bin/env python

from flask import Flask
from flask_restful import Api

from TopicModeling.routes import Index

FLASK_PORT = 5003

app = Flask(__name__)
api = Api(app)


class TopicsServer:
    """
    Handle routing of search requests via a flask server
    """

    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.add_routes()

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

        self.api.add_resource(Index, '/')
