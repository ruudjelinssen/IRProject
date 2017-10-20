import numpy as np
import math
import pyLDAvis
import pyLDAvis.gensim
from flask import request, render_template
from flask.views import View
from flask_restful import Resource

from TopicModeling import preprocessing
from TopicModeling.models import MIN_PAPER_TOPIC_PROB_THRESHOLD
from common.database import DataBase

# Database

db = DataBase('dataset/database.sqlite')


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
		papers = db.get_all_papers()

		if id >= len(self.topics):
			return {'error': 'No topic with id {}'.format(id)}

		relevant_papers = [(i, p) for i, p in sorted(
			enumerate(self.paper_topic_probability_matrix[:, id]),
			key=lambda x: x[1],
			reverse=True) if p > MIN_PAPER_TOPIC_PROB_THRESHOLD]

		authors = db.get_all_authors()
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

		return {
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
	def __init__(self, visualization, **kwargs):
		self.visualization = visualization

	def dispatch_request(self):
		return render_template('empty.html', visualization=self.visualization)
