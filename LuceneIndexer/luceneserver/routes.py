#!/usr/bin/env python

from flask import request
from flask_restful import Resource

from .search import Search


class Authors(Resource):
    """The author API to be able to retrieve authors"""

    def get(self):
        query = request.args.get('query')

        # Query for all results if no query argument in the request URL is present

        if query is None:
            query = '*:*'

        results = Search(query).get_results('authors')
        return {'authors': results}


class Papers(Resource):
    """The author API to be able to retrieve authors"""

    def get(self):
        query = request.args.get('query')

        # Query for all results if no query argument in the request URL is present

        if query is None:
            query = '*:*'

        results = Search(query).get_results('papers')
        return {'papers': results}
