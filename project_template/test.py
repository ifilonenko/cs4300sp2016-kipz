from __future__ import print_function
from .models import Docs
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import defaultdict
from collections import Counter
from numpy import linalg as LA
import matplotlib.pyplot as plt


### READ PRECOMPUTED VALUES
beer_sims = np.load("jsons/beer_sims.npy")
file1 = open("jsons/beer_name_to_index.json")
beer_name_to_index = json.load(file1)
file2 = open("jsons/beer_index_to_name.json")
beer_index_to_name = json.load(file2)
print(beer_name_to_index)
doc_voc_matrix = np.load("jsons/doc_voc_matrix.npy")


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

def find_similar(q):
	print("hello")
	return top_similar(q)