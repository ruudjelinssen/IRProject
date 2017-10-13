import logging

import gensim
from gensim.models import LdaModel

from TopicModeling import preprocessing
from common.database import DataBase

LDA_MODEL_FILE = 'lda.model'
DTM_MODEL_FILE = 'dtm.model'


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

    model = gensim.models.wrappers.DtmModel('dtm-win64.exe', corpus, time_slices, num_topics=20, id2word=dictionary)
    top_topics = model.top_topics(corpus)

    logging.info('Top topics:')
    logging.info(top_topics)


if __name__ == '__main__':
    # Test your models here
    # Moves to the topics_entry.py when everything is finished
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    corpus, dictionary = preprocessing.get_from_file_or_build()
    LDA(corpus, dictionary)
