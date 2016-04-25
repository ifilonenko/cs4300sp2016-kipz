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
import operator
import io

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
beer_name_to_index = json.load(file1, encoding='utf8')
file2 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/beer_index_to_name.json')
beer_index_to_name = json.load(file2, encoding='utf8')
# file3 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/beer_sims.json')
# beer_sims = json.load(file3, object_hook=json_numpy_obj_hook)
# file4 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/doc_voc_matrix.json')
# doc_voc_matrix = json.load(file4, object_hook=json_numpy_obj_hook)
file3 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/beers_compressed.json')
beers_compressed = json.load(file3, object_hook=json_numpy_obj_hook, encoding='utf8')
file4 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/features_compressed.json')
features_compressed = json.load(file4, object_hook=json_numpy_obj_hook, encoding='utf8')
file5 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/index_to_vocab.json')
index_to_vocab = json.load(file5, object_hook=json_numpy_obj_hook, encoding='utf8')
file6 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/vocab_to_index.json')
vocab_to_index = json.load(file6, object_hook=json_numpy_obj_hook, encoding='utf8')


def closest_beers(beers_set, beer_index_in, k = 5):
    beers_compressed = normalize(beers_set, axis = 1)
    beers_vector = beers_compressed[beer_index_in,:]
    sims = (np.dot(beers_compressed,beers_vector))/(LA.norm(beers_compressed)* LA.norm(beers_vector))
    asort = np.argsort(-sims)[:k+1]
    result = []
    for i in asort[1:]:
        result.append(beer_index_to_name[i])
    return result

def closest_features(features_set, feature_index_in, k = 5):
    features_compressed = normalize(features_set.T, axis = 1)
    feature_vector = features_compressed[feature_index_in,:]
    sims = (np.dot(features_compressed,feature_vector))/(LA.norm(features_compressed)* LA.norm(feature_vector))
    asort = np.argsort(-sims)[:k+1]
    result = []
    for i in asort[1:]:
        if i == feature_index_in:
            continue
        result.append((index_to_vocab[str(i)],sims[i]/sims[asort[0]]))
    return result

def rocchio(q, relevant, irrelevant, a=.3, b=.3, c=.8, clip = True):
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
    beers_vector = beers_compressed[beer_name_to_index[q],:]
    relevant_vectors = [beers_compressed[beer_name_to_index[x],:] for x in relevant] 
    relevant_vector = sum(x for x in relevant_vectors)
    irrelevant_vectors =[beers_compressed[beer_name_to_index[x],:] for x in irrelevant]  
    irrelevant_vector = sum(x for x in irrelevant_vectors)
    
    first_term = (a*beers_vector)
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
    pseudo_relevant = closest_beers(beers_compressed,beer_name_to_index[q],10)
    query_vector = rocchio(q,pseudo_relevant,[])
    beers_compressed_2 = normalize(beers_compressed, axis = 1)
    sims = (np.dot(beers_compressed_2,query_vector))/(LA.norm(beers_compressed_2)* LA.norm(query_vector))
    asort = np.argsort(-sims)[:k+1]
    result = []
    for i in asort[1:]:
        if beer_index_to_name[i] == q:
            continue
        result.append((beer_index_to_name[i],sims[i]/sims[asort[0]]))
    return result

def find_similar(q):
    queries = q.split(", ")
    query_list = defaultdict(list)
    result_list = defaultdict(list)
    final_result = {}
    for query in queries:
        if query in beer_index_to_name:
            query_list["beer"].append(query)
        elif query in vocab_to_index.keys():
            query_list["features"].append(query)
        else:
           return ["We don't have %s in our system" % query] 
    for key,value in query_list.iteritems():
        if key == "beer":
            for indx in value:
                for elem in roccio_with_pseudo(indx, 50):
                    result_list[elem[0].encode('utf-8')].append(elem[1]*100)
    for k,v in result_list.iteritems():
        final_result[k] = sum(v)
    print(final_result)
    return sorted(final_result.items(), key=operator.itemgetter(1), reverse=True)

def find_similar_features(q):
    if q not in vocab_to_index.keys():
        return ["We don't have this feature"]
    return closest_features(features_compressed, vocab_to_index[q], 50)
