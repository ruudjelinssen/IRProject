import os

from gensim import corpora

from TopicModeling.modeling import LDAModel
from TopicModeling.preprocessing import *
from common.database import DataBase

base_dir = os.path.join(os.path.dirname(__file__), 'modelfiles')

dictionary_file = os.path.join(base_dir, 'documents.dict')
corpus_file = os.path.join(base_dir, 'corpus.mm')
lda_filename = os.path.join(base_dir, 'model.lda')

# Load from file if available
if os.path.exists(dictionary_file) and os.path.exists(corpus_file):
    dictionary = corpora.Dictionary.load(dictionary_file)
    corpus = corpora.MmCorpus(corpus_file)
else:
    # Read from database
    db = DataBase('../dataset/database.sqlite')
    authors = db.get_all_authors()

    papers = db.get_all()

    documents = []

    for id, paper in papers.items():
        documents.append(paper.paper_text)

    documents = [[word for word in text.lower().split()] for text in documents]

    # Preprocess the documents
    preprocessor = MultiPreprocessor(documents,
                                     [StopWordsPreprocessor, MinFrequencyPreprocessor, SpecialCharactersPreprocessor])
    documents = preprocessor.run()

    # Create a dictionary (word to id)
    dictionary = corpora.Dictionary(documents)

    # Create corpus (doc to id to frequency)
    corpus = [dictionary.doc2bow(text) for text in documents]

# Load model from file
if os.path.exists(lda_filename):
    lda_model = LDAModel.from_model_file(lda_filename)
else:
    lda_model = LDAModel(dictionary=dictionary, corpus=corpus)
    lda_model.build_model(num_topics=20)


# Save files
lda_model.save_files(corpus_file, dictionary_file)
lda_model.save_model_file(lda_filename)

# Print the topics
i = 0
for topic in lda_model.model.show_topics(num_topics=20, formatted=False):
    i = i + 1
    print("Topic #" + str(i) + ":")
    for word in topic[1]:
        print('{} ({})'.format(word[0], word[1]))
    print("")
