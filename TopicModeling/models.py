import logging
import re

import gensim
import os
import pyLDAvis
import pandas as pd

import numpy as np
from gensim.models import LdaModel

from TopicModeling import preprocessing
from common.database import DataBase
from pprint import pprint

base_dir = os.path.join(os.path.dirname(__file__), 'modelfiles')
LDA_MODEL_FILE = os.path.join(base_dir, 'lda.model')
DTM_MODEL_FILE = os.path.join(base_dir, 'dtm.model')
ATM_MODEL_FILE = os.path.join(base_dir, 'atm.model')
SERIALIZATION_FILE = os.path.join(base_dir, 'atm-ser.model')
SPARSE_SIMILARITY_FILE = os.path.join(base_dir, 'sparse_similarity.index')
DOC_SIMILARITY_FILE = os.path.join(base_dir, 'doc_similarity.matrix')


# def LDA(corpus, dictionary):
# 	logging.info('Building LDA model.')
#
# 	# The parameters for the lda model
# 	num_topics = 30
# 	chunk_size = 7000
# 	passes = 20
# 	iterations = 400
# 	eval_every = None
#
# 	# Create the moddel
# 	model = LdaModel(corpus=corpus, id2word=dictionary, chunksize=chunk_size,
# 	                 alpha='auto', eta='auto',
# 	                 iterations=iterations, num_topics=num_topics,
# 	                 passes=passes, eval_every=eval_every)
#
# 	# Save the model to a file
# 	model.save(LDA_MODEL_FILE)
#
# 	# Get the top models
# 	top_topics = model.top_topics(corpus, num_words=30)
#
# 	# Calculate the average coherence
# 	avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
#
# 	logging.info('Average topic coherence: {}'.format(avg_topic_coherence))
# 	logging.info('Top topics:')
# 	logging.info(top_topics)


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
    top_topics = model.show_topics()

    logging.info('Top topics:')
    logging.info(top_topics)

    model_vis_atri = model.dtm_vis(corpus,time=29)


    DTM_vis = pyLDAvis.prepare(doc_lengths=model_vis_atri[2],doc_topic_dists=model_vis_atri[0],topic_term_dists=model_vis_atri[1],vocab=model_vis_atri[4],term_frequency=model_vis_atri[3])
    pyLDAvis.show(DTM_vis)


def ATM(corpus, dictionary, docno_to_index):
	logging.info('Building ATM model.')

	# The parameters for the lda model
	num_topics = 10
	chunk_size = 7000
	passes = 20
	iterations = 1
	eval_every = 0

	# TODO run multiple times to check what parameters are best (see ATM notebook)

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
		iterations=iterations,
		passes=passes,
		chunksize=chunk_size,
		eval_every=eval_every,
		serialized=True,
		serialization_path=SERIALIZATION_FILE
	)
	top_topics = model.top_topics(corpus)
	tc = sum([t[1] for t in top_topics])
	os.remove(SERIALIZATION_FILE)

	logging.info('Topic coherence: {}'.format(tc))

	# Save the model to a file
	model.save(ATM_MODEL_FILE)

	# Get the top models
	top_topics = model.top_topics(corpus, num_words=30)

	logging.info('Top topics:')
	logging.info(top_topics)


if __name__ == '__main__':
	# Test your models here
	# Moves to the topics_entry.py when everything is finished
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	corpus, dictionary, docno_to_index = preprocessing.get_from_file_or_build()
	# Simularity(corpus, dictionary)
	ATM(corpus, dictionary, docno_to_index)
# DTM(corpus, dictionary)
