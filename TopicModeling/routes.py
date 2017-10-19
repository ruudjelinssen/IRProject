from datetime import datetime
import numpy as np
from flask_restful import Resource
from TopicModeling.models import MIN_TOPIC_PROB_THRESHOLD

class BaseResource(Resource):
	def __init__(self, lda_model, corpus, dictionary, docno_to_index, paper_topic_probability_matrix):
		self.lda_model = lda_model
		self.corpus = corpus
		self.dictionary = dictionary
		self.docno_to_index = docno_to_index
		self.paper_topic_probability_matrix = paper_topic_probability_matrix


class Paper(BaseResource):
	"""The author API to be able to retrieve authors"""

	def get(self, id):

		# Get topics it belongs to
		topics = self.paper_topic_probability_matrix[self.docno_to_index[id]]
		topics = np.sort(topics)[::-1]

		# TODO name should give topic name, not ID
		return {'topics': [
			{
				'id': id,
				'name': id,
				'probability': prob
			} for id, prob in enumerate(topics) if prob > MIN_TOPIC_PROB_THRESHOLD
		]}
