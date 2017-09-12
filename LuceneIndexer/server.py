#!/usr/bin/env python

from flask import Flask, request
from flask_restful import Resource, Api

from luceneserver.indexer import Indexer
from luceneserver.search import Search

import lucene

app = Flask(__name__)
api = Api(app)


class Authors(Resource):
	"""The author API to be able to retrieve authors"""
	def get(self):

		query = request.args.get('query')

		# Query for all results if no query argument in the request URL is present

		if query is None:
			query = '*:*'

		results = Search().get_results(query)
		return {'authors': results}  # Fetches first column that is Employee ID

# Add our api resource routes

api.add_resource(Authors, '/authors')  # Route_1

# Run the application if running as a script

if __name__ == '__main__':

	# Always launch the Java VM in which we are going to run Lucene

	lucene.initVM(vmargs=['-Djava.awt.headless=true'])
	print('lucene', lucene.VERSION)

	# Index all documents on server startup

	indexer = Indexer().index_docs()

	# Start the server!

	app.run(port=5002)
	print('Server Running on port 5002')