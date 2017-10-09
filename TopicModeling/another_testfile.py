# Read from database
from nltk.tokenize import RegexpTokenizer

from common.database import DataBase

import nltk
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

from gensim.models import Phrases

# Add bigrams and trigrams to docs (only ones that appear 20 times or more).
bigram = Phrases(documents, min_count=20)
for idx in range(len(documents)):
    for token in bigram[documents[idx]]:
        if '_' in token:
            # Token is a bigram, add to document.
            documents[idx].append(token)

for doc in documents:
    print(doc[-10:])
