from collections import defaultdict

import numpy as np
import math
import pyLDAvis
import pyLDAvis.gensim
from bokeh.models import Range1d, LinearAxis
from bokeh.plotting import figure, show
from bokeh.embed import file_html, components
from flask import request, render_template
from flask.views import View
from flask_restful import Resource

from TopicModeling import preprocessing
from TopicModeling.models import MIN_PAPER_TOPIC_PROB_THRESHOLD
from TopicModeling.config import TOPICS
from common.database import DataBase


class BaseResource(Resource):
	"""Extend from this to give you access to these models and matrices.

	:param lda_model: Lda model
	:type lda_model: gensim.models.LdaModel
	:param corpus: The corpus
	:type corpus: gensim.corpora.MmCorpus
	:param dictionary: The dictionary
	:type dictionary: gensim.corpora.dictionary.Dictionary
	:param docno_to_index: Dictionary of paper id to index of corpus and matrix
	:type docno_to_index: dict
	:param paper_topic_probability_matrix: A matrix of papers x topics -> probability
	:type paper_topic_probability_matrix: np.array
	:param author_topic_probability_matrix: A matrix of author x topics -> probability
	:type author_topic_probability_matrix: np.array
	"""

	def __init__(self, lda_model, corpus, dictionary, docno_to_index, author2doc, author_short_names,
				 author_short_index_to_author, topics, paper_topic_probability_matrix, author_topic_probability_matrix):
		self.lda_model = lda_model
		self.corpus = corpus
		self.dictionary = dictionary
		self.docno_to_index = docno_to_index
		self.index_to_docno = dict((y, x) for x, y in self.docno_to_index.items())
		self.paper_topic_probability_matrix = paper_topic_probability_matrix
		self.author_topic_probability_matrix = author_topic_probability_matrix
		self.topics = topics
		self.author2doc = author2doc
		self.author_short_names = author_short_names
		self.author_short_index_to_author = author_short_index_to_author


class Paper(BaseResource):
	"""Returns topic information about a paper."""

	def get(self, id):
		# Database
		db = DataBase('dataset/database.sqlite')
		# Get topics it belongs to
		if id in self.docno_to_index:
			topics = self.paper_topic_probability_matrix[self.docno_to_index[id]]
			topics = np.sort(topics)[::-1]
			return {
				'id': id,
				'title': db.get_all_papers()[id].title,
				'topics': [{
					'id': id,
					'name': self.topics[id],
					'probability': prob
				} for id, prob in enumerate(topics) if prob > MIN_PAPER_TOPIC_PROB_THRESHOLD]
			}
		return {
			'error': 'Invalid id {}.'.format(id)
		}


class SearchTopic(BaseResource):
	def get(self):
		query = request.args.get('query', default='', type=str)
		topics = self.lda_model[self.dictionary.doc2bow(query.lower().split())]
		topics = sorted(topics, key=lambda x: x[1], reverse=True)
		return {'topics': [
			{
				'id': id,
				'name': self.topics[id],
				'probability': prob
			} for id, prob in topics if prob > (1 / len(self.topics) * 5)
		]}


class Topic(BaseResource):
	def get(self, id):
		# Database
		db = DataBase('dataset/database.sqlite')
		papers = db.get_all_papers()

		if id >= len(self.topics):
			return {'error': 'No topic with id {}'.format(id)}

		relevant_papers = [(i, p) for i, p in sorted(
			enumerate(self.paper_topic_probability_matrix[:, id]),
			key=lambda x: x[1],
			reverse=True) if p > MIN_PAPER_TOPIC_PROB_THRESHOLD]

		author_scores = []
		relevant_authors = []

		# TODO add more info
		probs = self.author_topic_probability_matrix[:, id]
		for i, prob in enumerate(probs):
			if not prob > 0.0:
				continue
			amount_of_papers = len(self.author2doc[self.author_short_names[i]])
			score = math.pow(prob, 2) * amount_of_papers
			if score > 1.0:
				author_scores.append((i, score, prob, amount_of_papers))

		author_scores.sort(key=lambda x: x[1], reverse=True)

		for i, score, prob, amount in author_scores[:10]:
			a_id, author = self.author_short_index_to_author[i]
			relevant_authors.append((a_id, author, score, prob, amount))

		top_words = []

		get_terms = self.lda_model.get_topic_terms(id, topn=10)
		for word_id,word_prob in  get_terms:
			word = self.dictionary[word_id]
			top_words.append([word,word_prob])

		return {
			'Top Words': [{
				'word': word,
				'prob': word_prob,
			} for word, word_prob in top_words],
			'papers': [{
				'id': self.index_to_docno[_id],
				'title': papers[self.index_to_docno[_id]].title,
				'probability': prob
			} for _id, prob in relevant_papers],
			'authors': [{
				'id': _id,
				'name': author.name,
				'score': score,
				'topic_probability': prob,
				'total_papers': amount
			} for _id, author, score, prob, amount in relevant_authors]
		}


class Author(BaseResource):
	def get(self, id):
		# Database
		db = DataBase('dataset/database.sqlite')
		authors = db.get_all_authors()

		if id in authors:
			name = authors[id].name
			names = list(self.author2doc.keys())
			topics = self.author_topic_probability_matrix[
				names.index(preprocessing.preproccess_author(name))
			]
			topics = np.sort(topics)[::-1]
			return {
				'id': id,
				'name': authors[id].name,
				'topics': [{
					'id': id,
					'name': self.topics[id],
					'probability': prob
				} for id, prob in enumerate(topics) if prob > MIN_PAPER_TOPIC_PROB_THRESHOLD]
			}
		return {
			'error': 'Invalid id {}.'.format(id)
		}


class Visualization(View):
	def __init__(self, visualization):
		self.visualization = visualization

	def dispatch_request(self):
		return render_template('empty.html', visualization=self.visualization)


class TopicEvolution(View):
	def __init__(self, year_topic_matrix):
		self.year_topic_matrix = year_topic_matrix

	def dispatch_request(self, id):
		data = self.year_topic_matrix[:, id]

		db = DataBase('dataset/database.sqlite')

		# Docs per year
		docs_per_year = {}
		for _id, paper in db.get_all_papers().items():
			if paper.year not in docs_per_year:
				docs_per_year[paper.year] = 0
			docs_per_year[paper.year] += 1

		# prepare some data
		x = [1987 + i for i in range(len(data))]
		y0 = data
		y1 = [y / docs_per_year[x + 1987] for x, y in enumerate(data)]

		# create a new plot
		p = figure(tools="", title="Evolution of \'{}\'".format(TOPICS[id]), x_axis_label='years',
				   y_axis_label='topic distribution'
	   	)

		p.extra_y_ranges = {'average':  Range1d(start=0, end=max(y1) * 1.05)}
		p.add_layout(LinearAxis(y_range_name='average'), 'right')

		# add some renderers
		p.vbar(x, top=y0, width=0.7, legend="Total")
		p.line(x, y=y1, line_width=2, legend="Average per paper", color="orange", y_range_name='average')

		# show the results
		script, div = components(p)

		return render_template('empty.html', visualization=div, script=script)
