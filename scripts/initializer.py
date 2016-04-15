from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import defaultdict
from collections import Counter
from numpy import linalg as LA
import base64
import json
import matplotlib.pyplot as plt

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


def get_sim(beer1, beer2):
    """
    Arguments:
        beer1: The name of the first beer we are looking for.
        beer2: The name of the second beer we are looking for.
    
    Returns:
        similarity: Cosine similarity of the two beer review(s).
    """
    doc_of_beer_1 = doc_voc_matrix[beer_name_to_index[beer1]]
    doc_of_beer_2 = doc_voc_matrix[beer_name_to_index[beer2]]   
    numerator = np.dot(doc_of_beer_1,doc_of_beer_2)
    return numerator/(LA.norm(doc_of_beer_1)* LA.norm(doc_of_beer_2))

file = open("beer_10000.json")
transcripts = json.load(file)
data = defaultdict(str)
for key in transcripts.keys():
    for review in transcripts[key]:
        data[key] += review['text'] + ' '

n_feats = 10000
doc_by_vocab = np.empty([len(data.keys()), n_feats])
#Code completion 1.1
tfidf_vec = TfidfVectorizer(input='context',stop_words='english', max_df=0.8, 
                            min_df=0.0162074554, max_features=10000, norm='l2')
tfidf_vec_scripts = []
beer_name_to_index = {}
beer_index_to_name = []
counter = 0
for key,value in data.iteritems():
    beer_name_to_index[key] = counter
    beer_index_to_name.append(key)
    tfidf_vec_scripts.append(value)
    counter+=1
doc_voc_matrix = tfidf_vec.fit_transform(tfidf_vec_scripts).toarray()
doc_by_vocab = doc_voc_matrix
index_to_vocab = {i:v for i, v in enumerate(tfidf_vec.get_feature_names())}
beer_sims = np.empty([len(data), len(data)], dtype = np.float32)
for beer1 in range(beer_sims.shape[0]):
    for beer2 in range(beer_sims.shape[1]):
        beer_sims[beer1,beer2] = (get_sim(beer_index_to_name[beer1], beer_index_to_name[beer2]))
print("--------------")
json.dump(beer_sims, open('beer_sims.json', 'w'), cls=NumpyEncoder)
print("HERE")
json.dump(beer_name_to_index, open('beer_name_to_index.json', 'w'))
print("NOW HERE")
json.dump(beer_index_to_name, open('beer_index_to_name.json', 'w'))
print("NOW HERE HERE")
json.dump(doc_voc_matrix, open('doc_voc_matrix.json', 'w'), cls=NumpyEncoder)
print("NOW HERE HERE HERE")



