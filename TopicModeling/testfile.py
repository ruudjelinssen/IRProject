import os
import string

from gensim import corpora, models
from gensim.models import AuthorTopicModel
from gensim.models.wrappers import dtmmodel

from common.database import DataBase

import stop_words

base_dir = os.path.join(os.path.dirname(__file__), 'modelfiles')

dictionary_file = os.path.join(base_dir, 'documents.dict')
corpus_file = os.path.join(base_dir, 'corpus.mm')
lda_filename = os.path.join(base_dir, 'model.lda')

# Create dictionary (word to id)
if os.path.exists(dictionary_file):
    dictionary = corpora.Dictionary.load(dictionary_file)
else:

    # Read documents

    db = DataBase('../dataset/database.sqlite')
    authors = db.get_all_authors()

    papers = db.get_all()

    documents = []

    for id, paper in papers.items():
        documents.append(paper.paper_text)

    # Tokenize and remove stopwords

    # remove common words and tokenize (I don't know if we have to do this by hand? There are a lot of words)
    stoplist = stop_words.safe_get_stop_words('en')
    special_ch = list(set(string.printable) - set(string.ascii_lowercase))
    docs = [[word for word in document.lower().split() if word not in stoplist]
             for document in documents]
    texts = []
    for document in docs:
        words = []
        for word in document:
            w = word
            for ch in special_ch:
                w = w.replace(ch, '')
            # Only use words of length a length of at least 2
            if len(w) > 1:
                words.append(w)
        texts.append(words)

    # remove words that appear only once
    from collections import defaultdict
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    # Save tokens that occur more than once
    texts = [[token for token in text if frequency[token] > 1]
             for text in texts]

    # Create dictionary
    dictionary = corpora.Dictionary(texts)
    dictionary.save(dictionary_file)

# Create corpus for each document (wordid to count)
if os.path.exists(corpus_file):
    corpus = corpora.MmCorpus(corpus_file)
else:
    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize(corpus_file, corpus)

# Create model
if os.path.exists(lda_filename):
    lda_model = models.LdaModel.load(lda_filename)
else:
    lda_model = models.LdaModel(corpus, id2word=dictionary, num_topics=20)
    lda_model.save(lda_filename)

# Print the topics
i = 0
for topic in lda_model.show_topics(num_topics=20, formatted=False):
    i = i + 1
    print("Topic #" + str(i) + ":")
    for word in topic[1]:
        print('{} ({})'.format(word[0], word[1]))
    print("")

# Search topic by query
query = "Image recognition"
bow = dictionary.doc2bow(query.lower().split())
print('')
print('Topic probabilities for query \'{}\':'.format(query))
print(lda_model[bow])
