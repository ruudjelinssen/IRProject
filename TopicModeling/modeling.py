import abc

from gensim import corpora, models


class Model:
    __metaclass__ = abc.ABCMeta

    def __init__(self, dictionary=None, corpus=None, model=None):
        self.dictionary = dictionary
        self.corpus = corpus
        self.model = model

    def save_files(self, corpus_filename, dictionary_filename):
        """Saves the dictionary and the corpus."""
        corpora.MmCorpus.serialize(corpus_filename, self.corpus)
        self.dictionary.save(dictionary_filename)

    @abc.abstractmethod
    def build_model(self):
        """Builds the model."""
        raise NotImplemented()

    @abc.abstractmethod
    def save_model_file(self, model_filename):
        """Builds the model."""
        raise NotImplemented()

    @abc.abstractclassmethod
    def from_model_file(cls, model_filename):
        raise NotImplemented()

    @classmethod
    def from_files(cls, dictionary_file, corpus_file, **kwargs):
        return cls(corpora.Dictionary.load(dictionary_file), corpora.MmCorpus(corpus_file), **kwargs)


class LDAModel(Model):

    def build_model(self, **kwargs):
        self.model = models.LdaModel(self.corpus, id2word=self.dictionary, **kwargs)

    @classmethod
    def from_model_file(cls, model_filename):
        return cls(model=models.LdaModel.load(model_filename))

    def save_model_file(self, model_filename):
        self.model.save(model_filename)
