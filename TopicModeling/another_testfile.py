# Read from database
import os
from nltk.tokenize import RegexpTokenizer
from gensim.corpora import Dictionary
from common.database import DataBase
from gensim import corpora, models

import nltk

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

base_dir = os.path.join(os.path.dirname(__file__), 'modelfiles')
dictionary_file = os.path.join(base_dir, 'documents.dict')
corpus_file = os.path.join(base_dir, 'corpus.mm')

# nltk.download('all')

def preProcessing():

    db = DataBase('../dataset/database.sqlite')
    papers = db.get_all_papers()

    documents = []

    for id, paper in papers.items():
        documents.append(paper.paper_text)

    # Split the documents into tokens.
    tokenizer = RegexpTokenizer(r'\w+')
    for idx in range(len(documents)):
        documents[idx] = documents[idx].lower()  # Convert to lowercase.
        documents[idx] = tokenizer.tokenize(documents[idx])  # Split into words.
    print("Completed Tokenizing")

    # Remove numbers, but not words that contain numbers.
    documents = [[token for token in doc if not token.isnumeric()] for doc in documents]

    # Remove words that are only one character.
    documents = [[token for token in doc if len(token) > 1] for doc in documents]

    from nltk.stem.wordnet import WordNetLemmatizer

    # Lemmatize all words in documents.
    lemmatizer = WordNetLemmatizer()
    documents = [[lemmatizer.lemmatize(token) for token in doc] for doc in documents]
    print("Completed Lemmanizing")

    from gensim.models.phrases import Phrases

    # Add bigrams and trigrams to docs (only ones that appear 20 times or more).
    bigram = Phrases(documents, min_count=20)
    for idx in range(len(documents)):
        for token in bigram[documents[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                documents[idx].append(token)

    # Remove rare and common tokens

    # Create a dictionary representation of the documents.
    dictionary = Dictionary(documents)

    # Filter out words that occur less than 20 documents, or more than 50% of the documents.
    dictionary.filter_extremes(no_below=30, no_above=0.4)

    corpus = [dictionary.doc2bow(doc) for doc in documents]

    #save the corpus file
    dictionary.save(dictionary_file)
    corpora.MmCorpus.serialize(corpus_file, corpus)

    print('Number of unique tokens: %d' % len(dictionary))
    print('Number of documents: %d' % len(corpus))

def makemodel():

    # dictionary = Dictionary.load(dictionary_file)
    dictionary = corpora.Dictionary.load(dictionary_file)
    corpus = corpora.MmCorpus(corpus_file)

    from gensim.models import LdaModel
    # Set training parameters.
    num_topics = 30
    chunksize = 7000
    passes = 5
    iterations = 400
    eval_every = None  # Don't evaluate model perplexity, takes too much time.

    model = LdaModel(corpus=corpus, id2word=dictionary, chunksize=chunksize,
                     alpha='auto', eta='auto',
                     iterations=iterations, num_topics=num_topics,
                     passes=passes, eval_every=eval_every)

    top_topics = model.top_topics(corpus)

    # Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
    avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
    print('Average topic coherence: %.4f.' % avg_topic_coherence)

    from pprint import pprint

    pprint(top_topics)

if not os.path.exists(dictionary_file) and not os.path.exists(corpus_file):
    preProcessing()
    makemodel()
else:
    makemodel()
