import numpy as np
import base64
import urllib
import json
from collections import defaultdict
from nltk.tokenize import TreebankWordTokenizer

def json_numpy_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.
    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct

file1000 = open("beer_1000.json")
beers = json.load(file1000)
data = defaultdict(str)
for key in beers.keys():
    for review in beers[key]:
        data[key] += review['text'] + ' '


tokenizer = TreebankWordTokenizer()
reviews_tokens = defaultdict(list)

for key in data.keys():
    toks = tokenizer.tokenize(data[key].replace('/', ' ')) #to separate cases like spicy/citrus/sweet
    toks_stripped = []
    for term in toks:
        toks_stripped.append(term.strip().strip('.').lower()) #to deal with cases like 'Light' and 'light.'
    reviews_tokens[key] = toks_stripped

def build_review_lengths(reviews):
    """ Builds an length dictionary from the beer reviews.
    
    reviews: dictionary of reviews for beers
        Each beer in this list already contains the tokenized review.
    Returns
    =======
    review_lengths: dict
        For each term, the index contains a list of
        tuples (doc_id, count_of_term_in_doc):
        index[term] = [(d1, tf1), (d2, tf2), ...]"""
    
    review_lengths = defaultdict(int)

    for key in reviews.keys():
        review_lengths[key] = len(reviews[key])
        
    return review_lengths

build_review_lengths(reviews_tokens)