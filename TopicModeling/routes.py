from datetime import datetime

from flask_restful import Resource


class BaseResource(Resource):
	def __init__(self, lda_model, corpus, dictionary, docno_to_index):
		self.lda_model = lda_model
		self.corpus = corpus
		self.dictionary = dictionary
		self.docno_to_index = docno_to_index


class Paper(BaseResource):
	"""The author API to be able to retrieve authors"""

	def get(self, id):
		return {'index': self.docno_to_index[id]}
