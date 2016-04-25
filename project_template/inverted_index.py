import numpy as np
import base64
import urllib
import json
from collections import defaultdict
from nltk.tokenize import TreebankWordTokenizer
from collections import Counter

file1000 = open("beer_1000.json")
beers = json.load(file1000)
data = defaultdict(str)
for key in beers.keys():
    for review in beers[key]:
        data[key] += review['text'] + ' '

file1 = urllib.urlopen('https://s3.amazonaws.com/stantemptesting/beer_name_to_index.json')
beer_name_to_index = json.load(file1)
file2 = urllib.urlopen('https://s3.amazonaws.com/stantemptesting/beer_index_to_name.json')
beer_index_to_name = json.load(file2)

def build_inverted_index(reviews):
    """ Builds an inverted index from the beer reviews.
    
    reviews: dictionary of reviews for beers
        Each beer in this list already contains the tokenized review.
    Returns
    =======
    index: dict
        For each term, the index contains a list of
        tuples (doc_id, count_of_term_in_doc):
        index[term] = [(d1, tf1), (d2, tf2), ...]
    Example
    =======
    
    >> test_idx = build_inverted_index([
    ...    {'toks': ['to', 'be', 'or', 'not', 'to', 'be']},
    ...    {'toks': ['do', 'be', 'do', 'be', 'do']}])
    
    >> test_idx['be']
    [(0, 2), (1, 2)]
    
    """
    inverted_index = defaultdict(list)
    
    for key in reviews.keys():
        beer_id = beer_name_to_index[key]
        counts = Counter(reviews[key])
        for term in counts:
            stripped_term = term.strip().strip('.').lower()
            if stripped_term:
                inverted_index[stripped_term].append((beer_id, counts[term]))
    return inverted_index


tokenizer = TreebankWordTokenizer()
reviews_tokens = defaultdict(list)

for key in data.keys():
    reviews_tokens[key] = tokenizer.tokenize(data[key].replace('/', ' '))

inv_index = build_inverted_index(reviews_tokens)