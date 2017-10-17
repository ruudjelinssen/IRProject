#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This file contains the code to create a simple REST server and be able to access defined paths
corresponding to the information that we want to retrieve
"""

from flask import Flask
from flask_restful import Api

from .routes import Papers
from .helpers.javavm import JavaVM


class LuceneServer:
    """
    Handle routing of search requests via a flask server
    """

    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.add_routes()

        @self.app.before_first_request
        def before_first_request():
            """Launch the Java VM before every first request when the server is (re)started"""
            JavaVM.init_vm()

    def init_flask_server(self, debug_mode_enabled):
        """
        Start a flask server instance
        :param debug_mode_enabled: whether the server should support live reload and verbose logging
        :return:
        """

        self.app.run(port=5002, debug=debug_mode_enabled)
        print('Server Running on port 5002')

    def add_routes(self):
        """
        Add our api resource routes
        :return:
        """

        self.api.add_resource(Papers, '/papers')
