import logging
import os
import re
import threading

import gensim
import math

import numpy as np
import pyLDAvis.gensim
from gensim.models import CoherenceModel, LdaModel

from TopicModeling import preprocessing
from common.database import DataBase

# The files
base_dir = os.path.join(os.path.dirname(__file__), 'modelfiles')
LDA_MODEL_FILE = os.path.join(base_dir, 'lda.model')
DTM_MODEL_FILE = os.path.join(base_dir, 'dtm.model')
ATM_MODEL_FILE = os.path.join(base_dir, 'atm.model')
SERIALIZATION_FILE = os.path.join(base_dir, 'atm-ser.model')
SPARSE_SIMILARITY_FILE = os.path.join(base_dir, 'sparse_similarity.index')
PAPER_TOPIC_MATRIX_FILE = os.path.join(base_dir, 'paper_topic.matrix')

# The parameters for the models
passes = 20
eval_every = 0
iterations = 100


def get_lda_coherence_scores(corpus, dictionary, _range=range(5, 100, 5)):
	"""Returns a list of coherence scores for different number of topics."""
	logging.info('Getting coherence scores from LDA models.')

	outputs = []

	# Loop over num_topics
	for i in _range:
		logging.info('Creating LDA model for num_topics={}.'.format(i))

		# Create the model
		model = LdaModel(corpus=corpus, id2word=dictionary, alpha='auto',
						 eta='auto', num_topics=i, passes=passes,
						 eval_every=eval_every)

		# Save the model to a file
		model.save('{}-{}-{}'.format(LDA_MODEL_FILE, 'test', i))

		# Create coherence model
		cm = CoherenceModel(model, corpus=corpus, dictionary=dictionary,
							coherence='u_mass')
		ch = cm.get_coherence()

		logging.info('Coherence for {} topics: {}'.format(i, ch))

		# Add to output
		outputs.append(
			(i, ch, model.show_topics())
		)

	return outputs


def visualize_model(model, corpus, dictionary, port=8000):
	vis = pyLDAvis.gensim.prepare(model, corpus, dictionary)
	pyLDAvis.show(vis, port=port)


def visualize_models(model_list, corpus, dictionary):
	i = 0
	for m in model_list:
		t = threading.Thread(target=visualize_model, args=(m, corpus, dictionary, 8000+i,))
		t.start()


def get_perplexity(model, chunk):
	log_perplexity = model.log_perplexity(chunk)
	perplexity = math.pow(2, -log_perplexity)
	return perplexity


def get_paper_topic_probabilities_matrix(model, corpus, dictionary, docno_to_index):
	"""Returns matrix of paper x topic where the value is the probability
	that paper belongs to the topic.

	:param model: LDA model
	:type model: gensim.models.LdaModel
	:param corpus: The corpus
	:type corpus: gensim.corpora.MmCorpus
	:param dictionary: The dictionary
	:type dictionary: gensim.corpora.dictionary.Dictionary
	:param docno_to_index: Dictionary from paper id to index in corpus
	:type docno_to_index: dict
	"""

	if os.path.exists(PAPER_TOPIC_MATRIX_FILE):
		logging.info('Using cached version of paper topic matrix. ({})'.format(PAPER_TOPIC_MATRIX_FILE))
		matrix = np.load(PAPER_TOPIC_MATRIX_FILE).item()
	else:
		logging.info('Creating paper topic matrix.')
		# Get papers from database
		db = DataBase('../dataset/database.sqlite')
		papers = db.get_all_papers()

		matrix = np.zeros(shape=(len(papers), model.num_topics))

		for _id, paper in papers.items():
			probs = model[corpus[docno_to_index[_id]]]
			for topic, prob in probs:
				matrix[docno_to_index[_id]][topic] = prob

		np.save(PAPER_TOPIC_MATRIX_FILE, matrix)

	return matrix


def get_lda_model(corpus, dictionary, num_topics):
	"""Create new model or use a cached one.

	:param corpus: The corpus
	:type corpus: gensim.corpora.MmCorpus
	:param dictionary: The dictionary
	:type dictionary: gensim.corpora.dictionary.Dictionary
	:param num_topics: When building the model, how many topics to use.
	:type num_topics: int
	:returns: The LDA model
	:rtype: gensim.models.LdaModel
	"""
	if os.path.exists(LDA_MODEL_FILE):
		logging.info(
			'Using cached version of LDA model. ({})'.format(LDA_MODEL_FILE))
		model = LdaModel.load(LDA_MODEL_FILE)
	else:
		logging.info('Building LDA model.')

		# Create the model
		model = LdaModel(corpus=corpus, id2word=dictionary, alpha='auto',
						 eta='auto', num_topics=num_topics, passes=passes,
						 eval_every=eval_every, iterations=iterations)

		# Save the model to a file
		model.save(LDA_MODEL_FILE)

		# Get the top models
		top_topics = model.top_topics(corpus[:200])

		# Calculate the average coherence
		avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
		log_perplexity = model.log_perplexity(corpus[:200])
		bound = model.bound(corpus[:200])

		logging.info('Average topic coherence: {}'.format(avg_topic_coherence))
		logging.info('Log perplexity: {}'.format(log_perplexity))
		logging.info('Bound: {}'.format(bound))
		logging.info('Top topics:')
		logging.info(top_topics)

	return model


# def DTM(corpus, dictionary):
# 	db = DataBase('../dataset/database.sqlite')
# 	papers = db.get_all_papers()
#
# 	# documents = []
# 	#
# 	# for id, paper in papers.items():
# 	#     documents.append(paper.year)
#
# 	my_time_list = [1987]
# 	for x in range(1, 30):
# 		my_time_list.append(my_time_list[0] + x)
# 	logging.debug(my_time_list)
#
# 	time_slices = []
# 	for year in my_time_list:
# 		papers_per_year = 0
# 		for id, paper in papers.items():
# 			if paper.year == year:
# 				papers_per_year = papers_per_year + 1
# 		time_slices.append(papers_per_year)
# 		logging.debug(sum(time_slices))
#
# 		model = gensim.models.wrappers.DtmModel('dtm-win64.exe', corpus,
# 												time_slices, num_topics=20,
# 												id2word=dictionary)
# 		top_topics = model.show_topics()
#
# 		logging.info('Top topics:')
# 		logging.info(top_topics)
#
# 		model_vis_atri = model.dtm_vis(corpus, time=29)
#
# 		DTM_vis = pyLDAvis.prepare(doc_lengths=model_vis_atri[2],
# 								   doc_topic_dists=model_vis_atri[0],
# 								   topic_term_dists=model_vis_atri[1],
# 								   vocab=model_vis_atri[4],
# 								   term_frequency=model_vis_atri[3])
# 		pyLDAvis.show(DTM_vis)


def get_atm_model(corpus, dictionary, docno_to_index, num_topics):
	"""Returns matrix of paper x topic where the value is the probability
	that paper belongs to the topic.


	:param corpus: The corpus
	:type corpus: gensim.corpora.MmCorpus
	:param dictionary: The dictionary
	:type dictionary: gensim.corpora.dictionary.Dictionary
	:param docno_to_index: Dictionary from paper id to index in corpus
	:type docno_to_index: dict
	:param num_topics: When building the model, how many topics to use.
	:type num_topics: int
	:returns: The ATM model
	:rtype: gensim.models.AuthorTopicModel
	"""
	if os.path.exists(ATM_MODEL_FILE):
		logging.info('Using cached version of ATM model. ({})'.format(ATM_MODEL_FILE))
		model = gensim.models.AuthorTopicModel.load(ATM_MODEL_FILE)
	else:
		logging.info('Building ATM model.')

		# Get all papers
		db = DataBase('../dataset/database.sqlite')
		papers = db.get_all()

		# Create doc to author dictionary
		author2doc = {}
		for _id, paper in papers.items():
			for author in paper.authors:
				# TODO: author names not always correct
				name = re.sub('\s', '', author.name)
				if name not in author2doc:
					author2doc[name] = []
				author2doc[name].append(docno_to_index[_id])
		logging.info('Number of different authors: {}'.format(len(author2doc)))

		# Create the model
		model = gensim.models.AuthorTopicModel(
			corpus,
			id2word=dictionary,
			num_topics=num_topics,
			author2doc=author2doc,
			alpha='auto',
			eta='auto',
			passes=passes,
			eval_every=eval_every,
			serialized=True,
			serialization_path=SERIALIZATION_FILE
		)

		# Save the model to a file
		model.save(ATM_MODEL_FILE)

		# Get the top models
		top_topics = model.top_topics(corpus[:200])

		# Calculate the average coherence
		avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
		log_perplexity = model.log_perplexity(corpus[:200])
		bound = model.bound(corpus[:200])

		logging.info('Average topic coherence: {}'.format(avg_topic_coherence))
		logging.info('Log perplexity: {}'.format(log_perplexity))
		logging.info('Bound: {}'.format(bound))
		logging.info('Top topics:')
		logging.info(top_topics)

	return model
