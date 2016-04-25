import numpy as np
import base64
import urllib
import json
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from numpy import linalg as LA

def json_numpy_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.
    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct

features_file = urllib.urlopen('https://s3.amazonaws.com/stantemptesting/features_compressed.json')
features_compressed = json.load(features_file, object_hook=json_numpy_obj_hook)

#Using beer_1000 because my computer cant handle any of the bigger files
#NEEDS TO BE CHANGED!!
file1000 = open("json/beer_1000.json")
beers = json.load(file1000)
data = defaultdict(str)
for key in beers.keys():
    for review in beers[key]:
        data[key] += review['text'] + ' '

n_feats = 1000
doc_by_vocab = np.empty([len(data.keys()), n_feats])
tfidf_vec = TfidfVectorizer(input='context',stop_words='english', max_df=0.8, 
                            min_df=0.0162074554, max_features=1000, norm='l2')
doc_voc_matrix = tfidf_vec.fit_transform(tfidf_vec_beers).toarray()

index_to_vocab = {i:v for i, v in enumerate(tfidf_vec.get_feature_names())}
print(index_to_vocab[0:5])
vocab_to_index = {v:i for i, v in enumerate(tfidf_vec.get_feature_names())}

def get_feature_sim(feature1, feature2):
    """
    Arguments:
        feature1: A word in the vocab of the beer reviews.
        feature2: Another word in the vocab of the beer reviews.
    
    Returns:
        similarity: Cosine similarity of the two beer features.
    """
    doc_of_feature_1 = np.transpose(features_compressed)[vocab_to_index[feature1]]
    doc_of_feature_2 = np.transpose(features_compressed)[vocab_to_index[feature2]]   
    numerator = np.dot(doc_of_feature_1,doc_of_feature_2)
    return numerator/(LA.norm(doc_of_feature_1)* LA.norm(doc_of_feature_2))

feature_sims = np.dot(np.transpose(features_compressed), features_compressed)

def top_similar(feature, k=10):
    """
        Arguments:
        feature: The beer characteristic that we are looking for
        k: Number of top terms to return
    
    Returns:
        result: List of the top k similar features 
    """
    feature_index = vocab_to_index[feature]
    filtered_s =  feature_sims[feature_index].argsort()[-(k+1):][::-1]
    result = []
    for elem in filtered_s:
        if elem != feature_index:
            result.append((index_to_vocab[elem],get_feature_sim(feature, index_to_vocab[elem])))
    return result

def closest_features(features_set, feature_index_in, k = 5):
    features_compressed = normalize(features_set, axis = 0)
    asort = np.argsort(-sims)[:k+1]
    result = []
    for i in asort[1:]:
        result.append((index_to_vocab[i],feature_sims[i]/feature_sims[asort[0]]))
    return result

def find_similar_features(q):
    print("Searching %d features" % len(index_to_vocab))
    return closest_features(features_compressed, vocab_to_index[q], 50)