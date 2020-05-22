#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 11:50:19 2020

@author: nsai
"""
import xlrd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from unicodedata import normalize
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import pandas as pd
## The general approach is to creat TF-IDF vectors and then using K-means for clustering

## Opening xlsx file 

wb = xlrd.open_workbook("/Users/nsai/Downloads/OneDrive_1_30-04-2020/Company Descriptions.xlsx")

longCompanyDescp = []
companyName = []

## Creating a List of company names and company description from the file 

for s in wb.sheets():
    for row in range(1,s.nrows,1):
            companyName.append(s.cell(row,0).value)
            if s.cell(row,2).value == "":
                longCompanyDescp.append(s.cell(row,1).value)
            else :
                longCompanyDescp.append(s.cell(row,2).value)
     
## Creating a dictionary of Company names and their description as k,v pairs

company_dict = dict(zip(companyName,longCompanyDescp))

##Cleaning description by removing stop words and numbers

def clean_descp(text):
    letters_only = re.sub('[^a-zA-Z]', ' ', text)
    words = letters_only.lower().split()
    new_words = []
    for w in words:
        w_norm = normalize('NFKD', w).encode('ASCII','ignore').decode('ASCII')
        new_words.append(w_norm)
    stopwords_eng = set(stopwords.words("english"))
    useful_words = [x for x in new_words if not x in stopwords_eng]
    
    # Combine words into a paragraph again
    
    useful_words_string = ' '.join(useful_words)
    return(useful_words_string)

clean_companyDescp = map(clean_descp,longCompanyDescp)
clean_company_dict = dict(zip(companyName,clean_companyDescp))


## Creating TF-IDF Vectors from the descriptions 


def tokenize(text):
    tokens = nltk.word_tokenize(text)
    #stems = stem_words(tokens, stemmer)
    return tokens

tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
tfs = tfidf.fit_transform(clean_company_dict.values())

#Finding Nearest Neighbours

model_tf_idf = NearestNeighbors(metric='cosine', algorithm='brute')
model_tf_idf.fit(tfs)

#Inputs a query tf_idf vector, the dictionary of companies, the knn model, and the number of neighbors
#Prints the k nearest neighbors

def print_nearest_neighbors(query_tf_idf, full_company_dictionary, knn_model, k):
    distances, indices = knn_model.kneighbors(query_tf_idf, n_neighbors = k+1)
    nearest_neighbors = [list(full_company_dictionary.keys())[x] for x in indices.flatten()]
    
    for company in range(len(nearest_neighbors)):
        if company == 0:
            print ('Query Company: {0}\n'.format(nearest_neighbors[company]))
        else:
            print ('{0}: {1}\n'.format(company, nearest_neighbors[company]))
        
print_nearest_neighbors(tfs[8], clean_company_dict, model_tf_idf, k=5)

## Calculating the right number of clusters by plotting 
## the Sum of Squared Errors for different clusters and finding the elbow

def find_optimal_clusters(data, max_k):
    iters = range(2, max_k+1, 4)
    sse = []
    for k in iters:
        sse.append(MiniBatchKMeans(n_clusters=k).fit(data).inertia_)
        print('Fit {} clusters'.format(k))
        
    f, ax = plt.subplots(1, 1)
    ax.plot(iters, sse, marker='o')
    ax.set_xlabel('Cluster Centers')
    ax.set_xticks(iters)
    ax.set_xticklabels(iters)
    ax.set_ylabel('SSE')
    ax.set_title('SSE by Cluster Center Plot')

find_optimal_clusters(tfs,40)

##Running k-means and plotting with k obtained from elbow method

k = 28
km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=5,
                verbose=1)
km.fit(tfs)

## Assigning cluster values to companies as a dictionary

cluster_assignment_dict = {}

for i in set(km.labels_):
    current_cluster_companies = [list(clean_company_dict.keys())[x] for x in np.where(km.labels_ == i)[0]]
    cluster_assignment_dict[i] = current_cluster_companies


## Assigning  Labels to clusters using description of companies in that cluster
cluster_themes_dict = {}

for key in cluster_assignment_dict.keys():
    current_tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
    current_tfs = current_tfidf.fit_transform(map(clean_descp,cluster_assignment_dict[key]))
    current_tf_idfs = dict(zip(current_tfidf.get_feature_names(), current_tfidf.idf_))
    tf_idfs_tuples = current_tf_idfs.items()
    cluster_themes_dict[key] = sorted(tf_idfs_tuples, key = lambda x: x[1])[:1]  

##Output format
    
compList = []
labelList = []
for v in cluster_assignment_dict.values():
    compList.append(v)

for values in cluster_themes_dict.values():
    labelList.append(values[0][0])

def createDict(label,comp):
    labelCol = []
    for i in range(len(comp)):
        labelCol.append(label)
    df  = pd.DataFrame(list(zip(labelCol,comp)),columns = ["Label","Company"])
    df.to_csv("/Users/nsai/Documents/Research/task3_2.csv",mode = "a")
    
for i in range(0,27,1):
    createDict(labelList[i],compList[i])