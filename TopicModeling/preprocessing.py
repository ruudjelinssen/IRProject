# This file is for preprocessing functions such as removing special characters, stop-words,
# words that are used in almost every document.
import abc
import string

import stop_words


class Preprocessor:
    """
    Preprocesses the documents to remove certain words.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, documents):
        self.documents = documents

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
        self.preprocessors = []
        for p in preprocessors:
            self.preprocessors.append(p(documents))

    def run(self):
        for p in self.preprocessors:
            self.documents = p.run()
        return self.documents


class SpecialCharactersPreprocessor(Preprocessor):
    """Remove special characters"""

    def run(self):
        special_ch = list(set(string.printable) - set(string.ascii_lowercase))
        docs = []
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
        return docs


class StopWordsPreprocessor(Preprocessor):
    """Remove words that are in the list of stopwords"""

    def run(self):
        stop_words_list = stop_words.safe_get_stop_words('en')
        docs = [[word for word in document.lower().split() if word not in stop_words_list]
                for document in self.documents]
        return docs


class MinFrequencyPreprocessor(Preprocessor):
    """Remove words that appear only x times"""

    def run(self):
        # remove words that appear only once
        from collections import defaultdict
        frequency = defaultdict(int)
        for text in self.documents:
            for token in text:
                frequency[token] += 1

        # Save tokens that occur more than once
        docs = [[token for token in text if frequency[token] > 1]
                for text in self.documents]
        return docs
