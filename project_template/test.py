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
import yaml

def json_numpy_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.

    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct

def ascii_encode_dict(data):
    ascii_encode = lambda x: x.decode('latin9').encode('utf8')
    return dict(map(ascii_encode, pair) for pair in data.items())

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
file7 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/review_lengths.json')
review_lengths = json.load(file7, object_hook=json_numpy_obj_hook, encoding='utf8')
file8 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/inv_index.json')
inv_index = json.load(file8, encoding='utf8')
file9 = urllib2.urlopen('https://s3.amazonaws.com/stantemptesting/beer_data_all.json')
beer_data_all = json.load(file9, encoding='utf8')


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
    pseudo_relevant = closest_beers(beers_compressed,beer_name_to_index[q],k)
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

def get_postings(int_arr):
    tuple_arr = []
    i = 0
    while i < (len(int_arr) - 1):
        tuple_arr.append((int_arr[i], int_arr[i+1]))
        i += 2
    return tuple_arr

def merge_postings(postings1,postings2):
    """Returns the intersection of postings1 and postings2 with the total count.

    """
    merged_posting = []
    i,j = 0,0
    while i < len(postings1) and j < len(postings2):
        if postings1[i][0] == postings2[j][0]:
            merged_posting.append((postings1[i][0], (postings1[i][1] + postings2[j][1])))
            i += 1
            j += 1
        elif postings1[i][0] < postings2[j][0]:
            i += 1
        else:
            j += 1
    return merged_posting

def beers_from_flavors(flavors, k):
    """ Returns the top k beers with these flavors.
    
    flavors: a list of flavors
    
    Returns
    beers: a dictionary of scores for each beer with these flavors and the flavors that beer has
    
    """
    alpha = 10.0
    postings = defaultdict(list)
    scores = defaultdict(float)
    beers_flavors = defaultdict(list)
    merged = []
    flavors = set(flavors)

    for flav in flavors:
        postings[flav] = get_postings(inv_index[flav])
        for beer_id, count in postings[flav]:
            scores[beer_index_to_name[beer_id]] += alpha*count/review_lengths[beer_index_to_name[beer_id]]
            beers_flavors[beer_index_to_name[beer_id]].append(flav)
            
    sorted_flavors = sorted(postings, key = lambda x: len(x), reverse=True)
    
    if len(sorted_flavors) > 1:
        merged = merge_postings(postings[sorted_flavors[0]], postings[sorted_flavors[1]])
        for beer_id, count in merged:
            scores[beer_index_to_name[beer_id]] += 10.0*alpha*count/review_lengths[beer_index_to_name[beer_id]]
        if len(sorted_flavors) > 2:
            i = 2
            while i < len(sorted_flavors):
                merged = merge_postings(merged, postings[sorted_flavors[i]])
                for beer_id, count in merged:
                    scores[beer_index_to_name[beer_id]] += (i*10)*alpha*count/review_lengths[beer_index_to_name[beer_id]]
                i += 1
    
    for beer_id, count in merged:
            scores[beer_index_to_name[beer_id]] = scores[beer_index_to_name[beer_id]]*len(flavors)
            
    sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)[:k]
    
    result = []
    for beer, score in sorted_scores:
        result.append((beer, score, beers_flavors[beer]))
    return result


def find_similar(q, number=5):
    queries = q.split(", ")
    query_list = defaultdict(list)
    result_list = defaultdict(list)
    final_result = {}
    for query in queries:
        query = query.strip().decode('utf-8').encode('ascii', 'replace')
        if query in beer_index_to_name:
            query_list["beer"].append(query)
        elif query in vocab_to_index.keys():
            query_list["features"].append(query)
        else:
           return ["We don't have %s in our system" % query] 
    for key,value in query_list.iteritems():
        if key == "beer":
            for indx in value:
                for elem in roccio_with_pseudo(indx, number):
                    result_list[elem[0].encode('utf-8')].append(elem[1]*100)
        if key == "features":
            for inx in beers_from_flavors(value, number):
                (beer_name, score, beer_flavors) = inx
                result_list[beer_name.encode('utf-8')].append(score*50)
    for k,v in result_list.iteritems():
        final_result[k] = sum(v)
    final_final_result = []
    sorted_result = sorted(final_result.items(), key=operator.itemgetter(1), reverse=True)
    for elem in sorted_result:
        beer_id, score = elem
        if beer_id in beer_data_all.keys(): ### ERROR WITH ENCODING
            beer_data = beer_data_all[beer_id]
            final_final_result.append([beer_id, score, beer_data])
    return final_final_result
