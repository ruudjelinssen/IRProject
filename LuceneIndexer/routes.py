#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Define the routes that we want the server to serve to the user
"""

from flask import request
from flask_restful import Resource

from luceneserver.search import Search


class Papers(Resource):
    """The author API to be able to retrieve authors"""

    def get(self):

        # Get the user input as teh query parameter called query

        query = request.args.get('query')

        # If a query is not present then it is the empty string

        if query is None:
            query = ''

        results = Search(query).get_results('papers')
        return results
