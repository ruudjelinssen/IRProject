# This file is for preprocessing functions such as removing special characters, stop-words,
# words that are used in almost every document.
import abc
import datetime
import heapq
import string
import time
from collections import Counter
from operator import itemgetter

import humanize
import stop_words
from gensim.models import TfidfModel


class Preprocessor:
    """
    Preprocesses the documents to remove certain words.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, documents):
        self.documents = documents
        self.count = len(documents)

    def run(self):
        start = time.time()
        print("Starting {}".format(self.__class__.__name__))
        docs = self._run()
        total = time.time() - start
        print("Finished {} in {}".format(self.__class__.__name__,
                                         humanize.naturaldelta(datetime.timedelta(seconds=total))))
        return docs

    @abc.abstractmethod
    def _run(self):
        """
        Runs the preprocessor

        :return: List of documents
        :rtype: list(list)
        """
        raise NotImplemented()


class MultiPreprocessor(Preprocessor):
    def __init__(self, documents, preprocessors):
        super(MultiPreprocessor, self).__init__(documents)
        self.preprocessors = preprocessors

    def _run(self):
        for p in self.preprocessors:
            self.documents = p(self.documents).run()
        return self.documents


class SpecialCharactersPreprocessor(Preprocessor):
    """Remove special characters"""

    def _run(self):
        special_ch = list(set(string.printable) - set(string.ascii_lowercase))
        docs = []
        i = 0
        for document in self.documents:
            words = []
            for word in document:
                w = word
                for ch in special_ch:
                    w = w.replace(ch, '')
                # Only use words of length a length of at least 2
                if len(w) > 1:
                    words.append(w)
            docs.append(words)
            i += 1
        return docs


class StopWordsPreprocessor(Preprocessor):
    """Remove words that are in the list of stopwords"""

    def _run(self):
        stop_words_list = stop_words.safe_get_stop_words('en')
        docs = [[word for word in document if word not in stop_words_list]
                for document in self.documents]
        return docs


class MinFrequencyPreprocessor(Preprocessor):
    """Remove words that appear only x times"""

    def _run(self):
        # remove words that appear only once
        from collections import defaultdict
        frequency = defaultdict(int)
        for text in self.documents:
            for token in text:
                frequency[token] += 1

        # Save tokens that occur more than once
        docs = [[token for token in doc if frequency[token] > 1]
                for doc in self.documents]
        return docs


class TopKWordsPreprocessor(Preprocessor):
    """Remove top k percent."""

    k = 0.05

    def _run(self):
        all_words = []

        for doc in self.documents:
            all_words.extend(doc)

        c = Counter(all_words)

        top_k_words, _ = zip(*c.most_common(int(len(c.items()) * self.k)))

        least_k_words, _ = zip(*least_common_values(c, int(len(c.items()) * self.k)))

        print(top_k_words)

        print(len(c.items()))

        to_remove = least_k_words + top_k_words

        docs = [[word for word in document if word not in to_remove]
                for document in self.documents]
        return docs


class TfIdfPreprocessor:
    def __init__(self, corpus):
        self.corpus = corpus

    def run(self):
        tfidf = TfidfModel(self.corpus)

        print(tfidf)

        # TODO: remove words from corpus

        return self.corpus


def least_common_values(counter, to_find=None):
    if to_find is None:
        return sorted(counter.items(), key=itemgetter(1), reverse=False)
    return heapq.nsmallest(to_find, counter.items(), key=itemgetter(1))
