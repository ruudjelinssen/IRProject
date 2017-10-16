import logging

import gensim
import os

import numpy as np
from gensim.models import LdaModel

from TopicModeling import preprocessing
from common.database import DataBase

base_dir = os.path.join(os.path.dirname(__file__), 'modelfiles')
LDA_MODEL_FILE = os.path.join(base_dir, 'lda.model')
DTM_MODEL_FILE = os.path.join(base_dir, 'dtm.model')
ATM_MODEL_FILE = os.path.join(base_dir, 'atm.model')
SERIALIZATION_FILE = os.path.join(base_dir, 'atm-ser.model')
SPARSE_SIMILARITY_FILE = os.path.join(base_dir, 'sparse_similarity.index')
DOC_SIMILARITY_FILE = os.path.join(base_dir, 'doc_similarity.matrix')


def LDA(corpus, dictionary):
	logging.info('Building LDA model.')

	# The parameters for the lda model
	num_topics = 30
	chunk_size = 7000
	passes = 20
	iterations = 400
	eval_every = None

	# Create the moddel
	model = LdaModel(corpus=corpus, id2word=dictionary, chunksize=chunk_size,
					 alpha='auto', eta='auto',
					 iterations=iterations, num_topics=num_topics,
					 passes=passes, eval_every=eval_every)

	# Save the model to a file
	model.save(LDA_MODEL_FILE)

	# Get the top models
	top_topics = model.top_topics(corpus, num_words=30)

	# Calculate the average coherence
	avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics

	logging.info('Average topic coherence: {}'.format(avg_topic_coherence))
	logging.info('Top topics:')
	logging.info(top_topics)


def DTM(corpus, dictionary):
	db = DataBase('../dataset/database.sqlite')
	papers = db.get_all_papers()

	# documents = []
	#
	# for id, paper in papers.items():
	#     documents.append(paper.year)

	my_time_list = [1987]
	for x in range(1, 30):
		my_time_list.append(my_time_list[0] + x)
	logging.debug(my_time_list)

	time_slices = []
	for year in my_time_list:
		papers_per_year = 0
		for id, paper in papers.items():
			if paper.year == year:
				papers_per_year = papers_per_year + 1
		time_slices.append(papers_per_year)
	logging.debug(sum(time_slices))

	model = gensim.models.wrappers.DtmModel('dtm-win64.exe', corpus,
											time_slices, num_topics=20,
											id2word=dictionary)
	top_topics = model.top_topics(corpus)

	logging.info('Top topics:')
	logging.info(top_topics)


def ATM(corpus, dictionary, docno_to_index):
	logging.info('Building ATM model.')

	# The parameters for the lda model
	num_topics = 30
	chunk_size = 7000
	passes = 20
	iterations = 400
	eval_every = None

	# TODO run multiple times to check what parameters are best (see ATM notebook)

	# Get all papers
	db = DataBase('../dataset/database.sqlite')
	papers = db.get_all()

	# Create doc to author dictionary
	author2doc = {}
	for _id, paper in papers.items():
		for author in paper.authors:
			# TODO: author names not always correct
			if author.name not in author2doc:
				author2doc[author.name] = []
			author2doc[author.name].append(docno_to_index[_id])
	logging.info('Number of different authors: {}'.format(len(author2doc)))

	# Create the model
	model = gensim.models.AuthorTopicModel(corpus,
										   id2word=dictionary,
										   num_topics=num_topics,
										   author2doc=author2doc,
										   alpha='auto', eta='auto',
										   iterations=iterations,
										   passes=passes,
										   chunksize=chunk_size,
										   eval_every=eval_every,
										   serialized=True,
										   serialization_path=SERIALIZATION_FILE)

	# Save the model to a file
	model.save(ATM_MODEL_FILE)

	# Get the top models
	top_topics = model.top_topics(corpus, num_words=30)

	# Calculate the average coherence
	avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics

	logging.info('Average topic coherence: {}'.format(avg_topic_coherence))
	logging.info('Top topics:')
	logging.info(top_topics)


def Simularity(corpus, dictionary):
	logging.info('Building sparse similarity matrix')

	index = gensim.similarities.docsim.SparseMatrixSimilarity(corpus, num_features=len(dictionary),
															  maintain_sparsity=True)

	logging.info('Finished building sparse similarity matrix')
	logging.info('Building matrix for document similarity')

	# Store everything in a #documents x #documents matrix
	similarity_matrix = np.zeros(shape=(len(corpus), len(corpus)))
	for i in range(0, len(corpus)):
		similarities = index[corpus[i]]
		for s in range(0, len(similarities)):
			if s != i:
				item = np.float64(similarities[s])
				similarity_matrix[i][s] = item

	logging.info('Finished building document similarity matrix')
	logging.info('Saving similarity files')

	index.save(SPARSE_SIMILARITY_FILE)
	np.save(DOC_SIMILARITY_FILE, similarity_matrix)


if __name__ == '__main__':
	# Test your models here
	# Moves to the topics_entry.py when everything is finished
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	corpus, dictionary, docno_to_index = preprocessing.get_from_file_or_build()
	# Simularity(corpus, dictionary)
	ATM(corpus, dictionary, docno_to_index)
# DTM(corpus, dictionary)
