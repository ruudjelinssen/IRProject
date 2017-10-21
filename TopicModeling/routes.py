from collections import defaultdict

import numpy as np
import math
import pyLDAvis
import pyLDAvis.gensim
from bokeh.models import Range1d, LinearAxis, ColumnDataSource
from bokeh.plotting import figure, show
from bokeh.embed import file_html, components
from flask import request, render_template
from flask.views import View
from flask_restful import Resource
from scipy.stats import gaussian_kde

from TopicModeling import preprocessing
from TopicModeling.models import MIN_PAPER_TOPIC_PROB_THRESHOLD
from TopicModeling.config import TOPICS, NUM_TOPICS
from common.database import DataBase


def calculate_score(prob, amount_of_papers):
	return prob * amount_of_papers


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
			topics = sorted([(i, prob) for i, prob in enumerate(topics)], key=lambda x: x[1], reverse=True)
			return {
				'id': id,
				'title': db.get_all_papers()[id].title,
				'topics': [{
					'id': id,
					'name': self.topics[id],
					'probability': prob
				} for id, prob in topics[:5] if prob > MIN_PAPER_TOPIC_PROB_THRESHOLD]
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
			} for id, prob in topics if prob > (1 / NUM_TOPICS * 5)
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
			score = calculate_score(prob, amount_of_papers)
			author_scores.append((i, score, prob, amount_of_papers))

		author_scores.sort(key=lambda x: x[1], reverse=True)

		for i, score, prob, amount in author_scores[:10]:
			a_id, author = self.author_short_index_to_author[i]
			relevant_authors.append((a_id, author, score, prob, amount))

		top_words = self.lda_model.show_topic(id, topn=20)

		return {
			'name': TOPICS[id],
			'words': [{
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
			print(names.index(preprocessing.preproccess_author(name)))
			topics = self.author_topic_probability_matrix[
				names.index(preprocessing.preproccess_author(name))
			]
			topics = sorted([(i, prob) for i, prob in enumerate(topics)], key=lambda x: x[1], reverse=True)
			return {
				'id': id,
				'name': authors[id].name,
				'topics': [{
					'id': id,
					'name': self.topics[id],
					'probability': prob
				} for id, prob in topics[:5] if prob > MIN_PAPER_TOPIC_PROB_THRESHOLD]
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


class TopicAuthorEvolution(View):

	TOP_N_AUTHORS = 20

	def __init__(self, year_author_topic_matrix, author_topic_probability_matrix, author2doc):
		self.year_author_topic_matrix = year_author_topic_matrix
		self.author_topic_probability_matrix = author_topic_probability_matrix
		self.author2doc = author2doc

	def dispatch_request(self, id):

		# List of short names
		author_short_list = list(self.author2doc.keys())

		# Get short_name -> name mapping
		db = DataBase('dataset/database.sqlite')
		author_mapping = {}
		for _id, author in db.get_all_authors().items():
			author_mapping[preprocessing.preproccess_author(author.name)] = author.name

		# Get top N authors in tuple (index, prob)
		author_scores = []
		probs = self.author_topic_probability_matrix[:, id]
		for i, prob in enumerate(probs):
			if not prob > 0.0:
				continue
			amount_of_papers = len(self.author2doc[author_short_list[i]])
			score = calculate_score(prob, amount_of_papers)
			author_scores.append((i, score, prob, amount_of_papers))
		author_scores.sort(key=lambda x: x[1], reverse=True)
		top_authors = author_scores[:self.TOP_N_AUTHORS]

		# Get values for each author
		top_authors_year_prob = self.year_author_topic_matrix[:, [x[0] for x in top_authors], id]

		cats = list([author_mapping[author_short_list[i]] for i, s, p, a in top_authors])

		p = figure(y_range=cats, plot_width=900, plot_height=900, x_range=(1986, 2017), toolbar_location=None)

		points_x = []
		points_y = []
		sizes = []
		for index, a in enumerate(top_authors):
			for year, score in enumerate(top_authors_year_prob[:, index]):
				points_x.append(year + 1987)
				print('{} {}'.format(index, author_short_list[a[0]]))
				points_y.append(index + 1)
				sizes.append(score * NUM_TOPICS * 2)
		p.circle(points_x, points_y, size=sizes, color='#4e88e5', alpha=0.65)

		p.outline_line_color = None
		p.background_fill_color = "#efefef"

		p.ygrid.grid_line_color = None
		p.xgrid.grid_line_color = "#dddddd"
		p.xgrid.ticker = p.xaxis[0].ticker

		p.axis.minor_tick_line_color = None
		p.axis.major_tick_line_color = None
		p.axis.axis_line_color = None

		# show the results
		script, div = components(p)

		return render_template('empty.html', visualization=div, script=script)


