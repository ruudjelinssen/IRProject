# This file is for preprocessing functions such as removing special characters, stop-words,
# words that are used in almost every document.
import abc
import string

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

    @abc.abstractmethod
    def run(self):
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

    def run(self):
        print("Starting MultiPreprocessor")
        for p in self.preprocessors:
            self.documents = p(self.documents).run()
        print("MultiPreprocessor finished")
        return self.documents


class SpecialCharactersPreprocessor(Preprocessor):
    """Remove special characters"""

    def run(self):
        print("Starting SpecialCharactersPreprocessor")
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
        print("SpecialCharactersPreprocessor finished")
        return docs


class StopWordsPreprocessor(Preprocessor):
    """Remove words that are in the list of stopwords"""

    def run(self):
        print("Starting StopWordsPreprocessor")
        stop_words_list = stop_words.safe_get_stop_words('en')
        docs = [[word for word in document if word not in stop_words_list]
                for document in self.documents]
        print("StopWordsPreprocessor finished")
        return docs


class MinFrequencyPreprocessor(Preprocessor):
    """Remove words that appear only x times"""

    def run(self):
        print("Starting MinFrequencyPreprocessor")
        # remove words that appear only once
        from collections import defaultdict
        frequency = defaultdict(int)
        for text in self.documents:
            for token in text:
                frequency[token] += 1

        # Save tokens that occur more than once
        docs = [[token for token in text if frequency[token] > 1]
                for text in self.documents]
        print("MinFrequencyPreprocessor finished")
        return docs


class TfIdfPreprocessor:
    def __init__(self, corpus):
        self.corpus = corpus

    def run(self):
        print("Running TF.IDF preprocessor")
        tfidf = TfidfModel(self.corpus)

        print(tfidf)

        # TODO: remove words from corpus

        print("Finished running TF.IDF preprocessor")
        return self.corpus
