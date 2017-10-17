import logging
import os
import re

import gensim
import pyLDAvis
from gensim.models import CoherenceModel, LdaModel

from TopicModeling import preprocessing
from common.database import DataBase

base_dir = os.path.join(os.path.dirname(__file__), 'modelfiles')
LDA_MODEL_FILE = os.path.join(base_dir, 'lda.model')
DTM_MODEL_FILE = os.path.join(base_dir, 'dtm.model')
ATM_MODEL_FILE = os.path.join(base_dir, 'atm.model')
SERIALIZATION_FILE = os.path.join(base_dir, 'atm-ser.model')
SPARSE_SIMILARITY_FILE = os.path.join(base_dir, 'sparse_similarity.index')
DOC_SIMILARITY_FILE = os.path.join(base_dir, 'doc_similarity.matrix')

# The parameters for the models
passes = 10
eval_every = 0


def get_lda_coherence_scores(corpus, dictionary, _range=(5, 100, 5), passes=10):
	logging.info('Getting coherence scores from LDA models.')

	outputs = []

	# Loop over num_topics
	for i in range(_range[0], _range[1], _range[2]):
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


def LDA(corpus, dictionary, num_topics):
	if os.path.exists(LDA_MODEL_FILE):
		logging.info(
			'Using cached version of LDA model. ({})'.format(LDA_MODEL_FILE))
		model = LdaModel.load(LDA_MODEL_FILE)
	else:
		logging.info('Building LDA model.')

		# Create the model
		model = LdaModel(corpus=corpus, id2word=dictionary, alpha='auto',
		                 eta='auto', num_topics=num_topics, passes=passes,
		                 eval_every=eval_every)

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

		model_vis_atri = model.dtm_vis(corpus, time=29)

		DTM_vis = pyLDAvis.prepare(doc_lengths=model_vis_atri[2],
		                           doc_topic_dists=model_vis_atri[0],
		                           topic_term_dists=model_vis_atri[1],
		                           vocab=model_vis_atri[4],
		                           term_frequency=model_vis_atri[3])
		pyLDAvis.show(DTM_vis)


def ATM(corpus, dictionary, docno_to_index, num_topics):
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


if __name__ == '__main__':
	# Test your models here
	# Moves to the topics_entry.py when everything is finished
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	corpus, dictionary, docno_to_index = preprocessing.get_from_file_or_build()

	scores = get_lda_coherence_scores(corpus, dictionary)
	print(scores)

	with open(os.path.join(base_dir, 'coherence.output'), 'w') as f:
		for s in scores:
			f.write('{}\t{}\t{}\n'.format(s[0], s[1], s[2]))
