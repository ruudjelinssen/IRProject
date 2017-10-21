#!/usr/bin/env python

import logging
import os

from flask import Flask
from flask_restful import Api

from TopicModeling import models
from TopicModeling.config import NUM_TOPICS, FLASK_PORT
from TopicModeling.routes import *

app = Flask(__name__, template_folder=os.path.join('TopicModeling', 'templates'))
api = Api(app)

# Database
db = DataBase('dataset/database.sqlite')


class TopicsServer:
	"""
	Handle routing of search requests via a flask server
	"""

	corpus = None
	dictionary = None
	docno_to_index = None
	lda_model = None
	atm_model = None
	author_topic_probability_matrix = None
	author2doc = None
	author_short_names = None
	author_short_index_to_author = None
	paper_topic_probability_matrix = None
	lda_visualization_html = None
	year_topic_matrix = None
	year_author_topic_matrix = None

	def __init__(self):
		self.app = Flask(__name__)
		self.api = Api(self.app)
		self.load_models()
		self.prepare_visualizations()
		self.add_routes()

	def load_models(self):
		"""Load all matrices and models in memory."""
		self.corpus, self.dictionary, self.docno_to_index = preprocessing.get_from_file_or_build()
		self.author2doc = models.get_author2doc()
		self.lda_model = models.get_lda_model(self.corpus, self.dictionary, NUM_TOPICS)
		self.author_short_names = list(self.author2doc.keys())
		self.author_short_index_to_author = {}
		for _id, author in db.get_all_authors().items():
			short = preprocessing.preproccess_author(author.name)
			if short in self.author_short_names:
				self.author_short_index_to_author[self.author_short_names.index(short)] = (_id, author)
		self.paper_topic_probability_matrix = models.get_paper_topic_probabilities_matrix(
			self.lda_model,
			self.corpus,
			self.dictionary,
			self.docno_to_index
		)
		self.author_topic_probability_matrix = models.get_author_topic_probabilities_matrix(
			self.paper_topic_probability_matrix,
			self.author2doc,
			self.docno_to_index
		)
		self.year_topic_matrix = models.get_year_topic_matrix(self.paper_topic_probability_matrix, self.docno_to_index)
		self.year_author_topic_matrix = models.get_year_author_topic_matrix(self.paper_topic_probability_matrix, self.docno_to_index, self.author2doc)

	def prepare_visualizations(self):
		"""Prepare LDA visualization."""
		vis = pyLDAvis.gensim.prepare(self.lda_model, self.corpus, self.dictionary)
		self.lda_visualization_html = pyLDAvis.prepared_data_to_html(vis)

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
		self.app.add_url_rule('/visualization/lda/', view_func=Visualization.as_view('lda_vis', visualization=self.lda_visualization_html))
		self.app.add_url_rule('/visualization/topicevolution/<int:id>/', view_func=TopicEvolution.as_view('topic_evolution', year_topic_matrix=self.year_topic_matrix))
		self.app.add_url_rule('/visualization/authortopicevolution/<int:id>/',
	  		view_func=TopicAuthorEvolution.as_view('author_topic_evolution',
		 		year_author_topic_matrix=self.year_author_topic_matrix,
		   		author_topic_probability_matrix=self.author_topic_probability_matrix,
		  		author2doc=self.author2doc
		  	))
		self._add_resource(Paper, '/paper/<int:id>/')
		self._add_resource(SearchTopic, '/topic')
		self._add_resource(Topic, '/topic/<int:id>/')
		self._add_resource(Author, '/author/<int:id>/')

	def _add_resource(self, resource, url):
		args = (
			self.lda_model,
			self.corpus,
			self.dictionary,
			self.docno_to_index,
			self.author2doc,
			self.author_short_names,
			self.author_short_index_to_author,
			TOPICS,
			self.paper_topic_probability_matrix,
			self.author_topic_probability_matrix
		)

		self.api.add_resource(resource, url, resource_class_args=args)
