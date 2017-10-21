#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Define the routes that we want the server to serve to the user
"""

from flask import request
from flask_restful import Resource

from .luceneserver.search import Search


class Papers(Resource):
    """The author API to be able to retrieve authors"""

    def get(self):

        # Get the user input as teh query parameter called query

        query_args = request.args

        results = Search(query_args).get_results('papers')
        return results

class Authors(Resource):
    """The author API to be able to retrieve authors"""

    def get(self):

        # Get the user input as teh query parameter called query

        query_args = request.args

        results = Search(query_args).get_results('authors')
        return results
