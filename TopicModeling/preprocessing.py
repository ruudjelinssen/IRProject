import logging
import os
import re

import nltk
import numpy as np
from gensim import corpora
from gensim.models.phrases import Phrases
from gensim.parsing import strip_punctuation, strip_multiple_whitespaces, strip_short, remove_stopwords, strip_numeric, \
	utils
from nltk import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer

from common.database import DataBase

base_dir = os.path.join(os.path.dirname(__file__), 'modelfiles')
dictionary_file = os.path.join(base_dir, 'documents.dict')
corpus_file = os.path.join(base_dir, 'corpus.mm')
docno_to_index_file = os.path.join(base_dir, 'docno_to_index.npy')

# Settings for the preproccessor
BIGRAM_MIN_FREQ = 20
EXTREME_NO_BELOW = 60
EXTREME_NO_ABOVE = 0.5

db = DataBase('../dataset/database.sqlite')


def _build_corpus_and_dictionary():
	"""Builds the corpus and dictionary. Returns both at the end."""
	logging.info('Getting the corpus and dictionary.')

	# Download language packs for the lemmanizing step
	logging.info('Downloading library for nltk lemmanizer.')
	nltk.download('all', quiet=True)
	logging.info('Finished downloading.')

	# Get from the database
	papers = db.get_all_papers()

	logging.info('Importing and preprocessing documents.')
	# Get the paper texts in a list
	documents = []
	docno_to_index = {}
	i = 0
	for _id, paper in papers.items():
		docno_to_index[_id] = i
		i += 1
		s = utils.to_unicode(paper.paper_text)
		for f in [lambda x: x.lower(), strip_punctuation, strip_multiple_whitespaces, strip_numeric, remove_stopwords, strip_short]:
			s = f(s)
		documents.append(s)

	# Split the documents into tokens.
	logging.info('Tokenizer started.')
	tokenizer = RegexpTokenizer(r'\w+')
	for idx in range(len(documents)):
		documents[idx] = documents[idx]
		documents[idx] = tokenizer.tokenize(documents[idx])
	logging.info('Finished tokenizing the texts.')

	# Remove numbers, but not words that contain numbers.
	logging.info('Removing numeric tokens.')
	documents = [[token for token in doc if not token.isnumeric()] for doc in documents]
	logging.info('Numeric tokens removed.')

	# Remove words that are only one character.
	logging.info('Removing tokens that consist of 1 character.')
	documents = [[token for token in doc if len(token) > 1] for doc in documents]
	logging.info('Finished removing tokens that consist of 1 character.')

	# Lemmatize all words in documents.
	logging.info('Lemmanizing tokens from the nltk package.')
	lemmatizer = WordNetLemmatizer()
	documents = [[lemmatizer.lemmatize(token) for token in doc] for doc in documents]
	logging.info('Lemmanizer complete')

	# Add bigrams and trigrams to docs (only ones that appear BIGRAM_MIN_FREQ times or more).
	logging.info('Creating bigrams of pairs of words that appear at least {} times.'.format(BIGRAM_MIN_FREQ))
	bigram = Phrases(documents, min_count=BIGRAM_MIN_FREQ)
	for idx in range(len(documents)):
		for token in bigram[documents[idx]]:
			# Add bigrams to the documents
			if '_' in token:
				documents[idx].append(token)
	logging.info('Finished creating bigrams.')

	# Build dictionary from documents
	dictionary = corpora.Dictionary(documents)

	# Remove extreme words (appear a lot of times, or only few times)
	dictionary.filter_extremes(no_below=EXTREME_NO_BELOW, no_above=EXTREME_NO_ABOVE)

	# Create a corpus from the documents
	corpus = [dictionary.doc2bow(doc) for doc in documents]

	# Save them as a file
	dictionary.save(dictionary_file)
	corpora.MmCorpus.serialize(corpus_file, corpus)
	np.save(docno_to_index_file, docno_to_index)

	logging.info('Finished creating corpus and dictionary.')
	logging.info('Number of unique tokens: {}'.format(len(dictionary)))
	logging.info('Number of documents: {}'.format(len(corpus)))


def get_from_file_or_build():
	"""Returns the corpus and dictionary. Builds them if needed."""

	if not os.path.exists(dictionary_file) or not os.path.exists(
			corpus_file) or not os.path.exists(docno_to_index_file):
		logging.info('Corpus and dictionary file do not exist')
		_build_corpus_and_dictionary()
	else:
		logging.info(
			'Using corpus and dictionary that have already been build.')

	dictionary = corpora.Dictionary.load(dictionary_file)
	corpus = corpora.MmCorpus(corpus_file)
	docno_to_index = np.load(docno_to_index_file).item()

	papers = db.get_all_papers()
	if len(papers) != len(corpus):
		raise Exception(
			'Amount of papers in database is not equal to corpus length. database: {}, corpus: {}'.format(
				len(papers), len(corpus)))

	logging.info('Number of unique tokens: {}'.format(len(dictionary)))
	logging.info('Number of documents: {}'.format(len(corpus)))

	return corpus, dictionary, docno_to_index
