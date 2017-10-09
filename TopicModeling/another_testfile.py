# Read from database
from nltk.tokenize import RegexpTokenizer

from common.database import DataBase

import nltk

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

nltk.download('all')

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

# Remove numbers, but not words that contain numbers.
documents = [[token for token in doc if not token.isnumeric()] for doc in documents]

# Remove words that are only one character.
documents = [[token for token in doc if len(token) > 1] for doc in documents]

from nltk.stem.wordnet import WordNetLemmatizer

# Lemmatize all words in documents.
lemmatizer = WordNetLemmatizer()
documents = [[lemmatizer.lemmatize(token) for token in doc] for doc in documents]

from gensim.models.phrases import Phrases

# Add bigrams and trigrams to docs (only ones that appear 20 times or more).
bigram = Phrases(documents, min_count=20)
for idx in range(len(documents)):
    for token in bigram[documents[idx]]:
        if '_' in token:
            # Token is a bigram, add to document.
            documents[idx].append(token)

# Remove rare and common tokens.
from gensim.corpora import Dictionary

# Create a dictionary representation of the documents.
dictionary = Dictionary(documents)

# Filter out words that occur less than 20 documents, or more than 50% of the documents.
dictionary.filter_extremes(no_below=20, no_above=0.5)

corpus = [dictionary.doc2bow(doc) for doc in documents]

print('Number of unique tokens: %d' % len(dictionary))
print('Number of documents: %d' % len(corpus))

from gensim.models import LdaModel

# Set training parameters.
num_topics = 10
chunksize = 2000
passes = 20
iterations = 400
eval_every = None  # Don't evaluate model perplexity, takes too much time.

# Make a index to word dictionary.
temp = dictionary[0]  # This is only to "load" the dictionary.
id2word = dictionary.id2token

model = LdaModel(corpus=corpus, id2word=id2word, chunksize=chunksize,
                 alpha='auto', eta='auto',
                 iterations=iterations, num_topics=num_topics,
                 passes=passes, eval_every=eval_every)

top_topics = model.top_topics(corpus, num_words=20)

# Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
print('Average topic coherence: %.4f.' % avg_topic_coherence)

from pprint import pprint

pprint(top_topics)
