from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import defaultdict
from collections import Counter
from numpy import linalg as LA
import base64
import json
import matplotlib.pyplot as plt
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
from nltk.tokenize import TreebankWordTokenizer

class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict 
        holding dtype, shape and the data, base64 encoded.
        """
        if isinstance(obj, np.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = np.ascontiguousarray(obj)
                assert(cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            data_b64 = base64.b64encode(obj_data)
            return dict(__ndarray__=data_b64,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder(self, obj)

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
    counter = 0
    for key in reviews.keys():
        print("%d, %d" % (counter, len(reviews.keys())))
        beer_id = beer_name_to_index[key]
        counts = Counter(reviews[key])
        for term in counts:
            if term in vocab_to_index.keys():
                inverted_index[term].append((beer_id, counts[term]))
        counter+=1
    return inverted_index

file = open("beer_all.json")
transcripts = json.load(file)
new_dict = defaultdict(list)
all_keys = transcripts.keys()
keys_length = len(all_keys)
counter = 0
print("ascii conversion")
print("================")
for key in all_keys[0:90]:
    print("%d, %d" % (counter, keys_length))
    new_key = key.encode('ascii', 'ignore')
    for index_dict in transcripts[key]:
        inner_dict = {}
        for k in index_dict.keys():
            inner_dict[k.encode('ascii', 'ignore')] = index_dict[k].encode('ascii', 'ignore')
        new_dict[new_key].append(inner_dict)
    counter+=1

new_transcripts = new_dict
json.dump(new_transcripts, open('new_transcripts_2.json', 'w'))
data = defaultdict(list)
text_data = defaultdict(str)
print("constructing beer_all_json and text_data")
print("================")
counter = 0
for key in new_transcripts.keys():
    print("%d/%d" % (counter, len(new_transcripts.keys())))
    review = new_transcripts[key][0]
    inner_dict = {}
    inner_dict['ABV'] = review['ABV']
    inner_dict['appearance'] = review['appearance']
    inner_dict['aroma'] = review['aroma']
    inner_dict['brewerId'] = review['brewerId']
    inner_dict['beerId'] = review['beerId']
    inner_dict['overall'] = review['overall']
    inner_dict['palate'] = review['palate']
    inner_dict['style'] = review['style']
    inner_dict['taste'] = review['appearance']
    inner_dict['appearance'] = review['taste']
    inner_dict['time'] = review['time']
    data[key] = inner_dict
    for review_index in new_transcripts[key]:
        text_data[key] += review_index['text'] + ' '
    counter+=1

print("================")
json.dump(data, open('beer_data_all_2.json', 'w'))
print("================")
json.dump(text_data, open('new_transcripts_text_2.json', 'w'))
print("=========")
n_feats = 10000
doc_by_vocab = np.empty([len(text_data.keys()), n_feats])
tfidf_vec = TfidfVectorizer(input='context',stop_words='english', max_df=0.8, 
                            min_df=0.0162074554, max_features=10000, norm='l2')
tfidf_vec_scripts = []
beer_name_to_index = {}
beer_index_to_name = []
counter = 0
print("contructing tfidf vectors, beer name and index")
print("=============")
for key,value in text_data.iteritems():
    print("%d/%d" % (counter, len(text_data.keys())))
    beer_name_to_index[key] = counter
    beer_index_to_name.append(key)
    tfidf_vec_scripts.append(value)
    counter+=1
json.dump(beer_name_to_index, open('beer_name_to_index_2.json', 'w'))
json.dump(beer_index_to_name, open('beer_index_to_name_2.json', 'w'))
print("computed beer_name and index")
doc_voc_matrix = tfidf_vec.fit_transform(tfidf_vec_scripts).toarray()
doc_by_vocab = doc_voc_matrix
print("transformed tfidf matrix")
json.dump(doc_voc_matrix, open('doc_voc_matrix_2.json', 'w'), cls=NumpyEncoder)
print("NOW HERE HERE HERE")
print("========================")
print("grabbing index_to_vocab and vocab_to_index")
index_to_vocab = {i:v for i, v in enumerate(tfidf_vec.get_feature_names())}
vocab_to_index = {v:i for i, v in enumerate(tfidf_vec.get_feature_names())}
json.dump(index_to_vocab, open('index_to_vocab_2.json', 'w'))
json.dump(vocab_to_index, open('vocab_to_index_2.json', 'w'))
print("computed vocab name and index")
print("========")
print("building review tokens")
tokenizer = TreebankWordTokenizer()
reviews_tokens = defaultdict(list)
for key in text_data.keys():
    toks = tokenizer.tokenize(text_data[key].replace('/', ' ')) #to separate cases like spicy/citrus/sweet
    toks_stripped = []
    for term in toks:
        toks_stripped.append(term.strip().strip('.').lower()) #to deal with cases like 'Light' and 'light.'
    reviews_tokens[key] = toks_stripped
print("building review_lengths")
review_lengths_data = build_review_lengths(reviews_tokens)
json.dump(review_lengths_data, open('review_lengths_2.json', 'w'))
print("computed review lengths")
print("building inverted index")
inv_index = build_inverted_index(reviews_tokens)
json.dump(inv_index, open('inv_index_2.json', 'w'))
print("computed inv index")
print("==================")
print("computing SVD")
beers_compressed, _, features_compressed = svds(doc_voc_matrix, k=80)
json.dump(beers_compressed, open('beers_compressed_2.json', 'w'), cls=NumpyEncoder)
json.dump(features_compressed, open('features_compressed_2.json', 'w'), cls=NumpyEncoder)
print("finished")

