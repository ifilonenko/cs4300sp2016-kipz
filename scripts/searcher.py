from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import defaultdict
from collections import Counter
from numpy import linalg as LA
import json
import matplotlib.pyplot as plt

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

def top_terms(n1, n2, k=10):
    """
    Arguments:
        n1: The name of the beer we are looking for.
        n2: The title of the second beer we are looking for.
        k: Number of top terms to return
    
    Returns:
        result: List of the top k similar terms between the
        two beer review(s).
    """
    beer1 = doc_voc_matrix[beer_name_to_index[n1]]
    beer2 = doc_voc_matrix[beer_name_to_index[n2]]
    return [ index_to_vocab[key] for key in np.multiply(beer1,beer2).argsort()[-k:][::-1] ]

def top_similar(beer, k=10):
    """
        Arguments:
        beer: The name of the beer we are looking for.
        k: Number of top terms to return
    
    Returns:
        result: List of the top k similar beers 

    """
    beer_index = beer_name_to_index[beer]
    filtered_s =  beer_sims[beer_index].argsort()[-(k+1):][::-1]
    result = []
    for elem in filtered_s:
        if elem != beer_index:
            result.append((beer_index_to_name[elem],get_sim(beer, beer_index_to_name[elem])))
    return result

def least_similar(beer, k=10):
    beer_index = beer_name_to_index[beer]
    filtered_s =  beer_sims[beer_index].argsort()[:(k+1)]
    result = []
    for elem in filtered_s:
        if elem != beer_index:
            result.append((beer_index_to_name[elem],get_sim(beer, beer_index_to_name[elem])))
    return result

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
np.save('beer_sims.npy', beer_sims)
json.dump(beer_name_to_index, open('beer_name_to_index.json', 'w'))
json.dump(beer_index_to_name, open('beer_index_to_name.json', 'w'))
np.save('doc_voc_matrix.npy', doc_voc_matrix)

print(top_similar('Red Moon'))

