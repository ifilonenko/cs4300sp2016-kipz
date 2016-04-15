from __future__ import print_function
from .models import Docs
import os
import base64
import json
import urllib2
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import defaultdict
from collections import Counter
from numpy import linalg as LA
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize

def json_numpy_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.

    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct

### READ PRECOMPUTED VALUES
file1 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/beer_name_to_index.json')
beer_name_to_index = json.load(file1)
file2 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/beer_index_to_name.json')
beer_index_to_name = json.load(file2)
# file3 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/beer_sims.json')
# beer_sims = json.load(file3, object_hook=json_numpy_obj_hook)
# file4 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/doc_voc_matrix.json')
# doc_voc_matrix = json.load(file4, object_hook=json_numpy_obj_hook)
file3 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/beers_compressed.json')
beers_compressed = json.load(file3, object_hook=json_numpy_obj_hook)
file4 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/features_compressed.json')
features_compressed = json.load(file4, object_hook=json_numpy_obj_hook)

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

def rocchio(query, relevant, irrelevant, a=.3, b=.3, c=.8, clip = True):
    '''
    Arguments:
        query: a string representing the name of the beer being queried for
        
        relevant: a list of strings representing the names of relevant beers for query
        
        irrelevant: a list of strings representing the names of irrelevant beers for query
        
        a,b,c: floats, corresponding to the weighting of the original query, relevant queries,
        and irrelevant queries, respectively.
        
        clip: boolean, whether or not to clip all returned negative values to 0
        
    Returns:
        q_mod: a vector representing the modified query vector. this vector should have no negatve
        weights in it!
    '''
    query_index = beer_name_to_index[query]
    relevant_vectors = [doc_voc_matrix[beer_name_to_index[x]] for x in relevant] 
    relevant_vector = sum(x for x in relevant_vectors)
    irrelevant_vectors =[doc_voc_matrix[_name_to_index[x]] for x in irrelevant]  
    irrelevant_vector = sum(x for x in irrelevant_vectors)
    
    first_term = (a*doc_voc_matrix[query_index])
    if not relevant:
        second_term = 0
    else:
        second_term = ((b*relevant_vector)/(len(set(relevant))))
    if not irrelevant:
        third_term = 0
    else:
        third_term = ((c*irrelevant_vector)/(len(set(irrelevant))))
    if clip:
        final = (first_term + second_term - third_term).clip(min=0)
    else:
        final = (first_term + second_term - third_term)
    return final

def roccio_with_pseudo(q, k = 10):
    '''
    Arguments:
        q: Name of the beer you are searching for
        
        k: int representing how many of the original ranking to treat as relevant results
        
    Returns:
        List of the top k similar terms between the
        two beer review(s).
    """
    '''
    mean_average_percision = []
    query_index = beer_name_to_index[q]
    query_initial_vector = doc_voc_matrix[query_index]
    cos_sim_init = np.array([ np.dot(query_initial_vector,vector) for vector in doc_voc_matrix ]).argsort()[::-1]
    cos_indexes_init = []
    for elem in cos_sim_init:
        if elem != beer_name_to_index[q]:
            cos_indexes_init.append(elem)
    pseudo_relevant = [beer_index_to_name[x] for x in cos_indexes_init][:k]
    query_vector = rocchio(q,pseudo_relevant,[])
    cos_sim = np.array([ np.dot(query_vector,vector) for vector in doc_voc_matrix ]).argsort()[::-1]
    cos_indexes = []
    for elem in cos_sim:
        if elem != beer_name_to_index[q]:
            cos_indexes.append(elem)
    return ([beer_index_to_name[x] for x in cos_indexes][:k])

def closest_projects(beers_set, project_index_in, k = 5):
    beers_compressed = normalize(beers_set, axis = 1)
    sims = beers_compressed.dot(beers_compressed[project_index_in,:])
    asort = np.argsort(-sims)[:k+1]
    result = []
    for i in asort[1:]:
        result.append((beer_index_to_name[i],sims[i]/sims[asort[0]]))
    return result

def find_similar(q):
	print("Searching %d beers" % len(beer_index_to_name))
	return closest_projects(beers_compressed, beer_name_to_index[q], 50)