#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 22:49:08 2020

@author: nsai

The final output should have a file with fields: 
year, filename, count of high competition (with its synonyms) 
and count of technological competition
"""

import urllib
import os
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.corpus import webtext
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import BigramCollocationFinder
from nltk.corpus import wordnet as wn

## Counter and Synonyms for High Competition and Technological Comeptition - Tried using Wordnet
## but synonyms for compound words are out of context

def synCounter(filepath,file,subdir):
    filename = file
    countHighComp = 0
    countTechComp = 0
    year = os.path.basename(subdir)
    synHighComp = {"high" : ["competition"],"heavy" :["competition"] ,"highly" : ["competitive"],
               "competitive" : ["pressures","pressure","markets","position"],
               "hard":["competition"],"very" : ["competitive"],"many": ["competitors","contenders"],
               "competition" : ["competition"],"face" : ["competition"]}

    synTechComp = {"technological" : ["competition","competence","capacity","competitors","competency","competitor"],
               "technical" : ["competence","competition","capacity","competitors","competency","competitor"]}

##Trying wordnet synonyms for competition

 #   for ss in wn.synsets('competition'):
 #       for l in ss.lemmas():
 #           print(l.name())
        
## Getting Text from HTML using BeautifulSoup4

    url = "file:///" + filepath
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,"lxml")
    text = soup.get_text()
    
##Cleaning text

    lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

##Moving text to new file

    file1 = open("/Users/nsai/Documents/Research/newfile.txt","w")
    file1.write(text)
    file1.close()

#Cleaning files for stopwords and punctuation

    words = [w.lower() for w in webtext.words("/Users/nsai/Documents/Research/newfile.txt")]#could just use "text" variable instead of a file
    bcf = BigramCollocationFinder.from_words(words)
    stopset = set(stopwords.words('english'))
    filter_stops = lambda w: len(w) < 3 or w in stopset
    bcf.apply_word_filter(filter_stops)

##Identifying Bigrams using Maximum Likelihood ratio

    bcf1 = (bcf.nbest(BigramAssocMeasures.likelihood_ratio, 6000))
    listToStr = " ".join(map(str,bcf1))
    file2 = open("/Users/nsai/Documents/Research/newfile2.txt","w")
    file2.write(listToStr)

##Convert List to Dict
    dictBCF = {}
    for (key, value) in bcf1:
        dictBCF.setdefault(key, []).append(value)
        
    wordListHighComp = []
    wordListTechComp = []
    
##Converting words to dictionary
    
    for k in dictBCF.keys() & synHighComp.keys():
        resHighCompKey = []
        resHighCompValue = []
        resDict = {}
        for v in synHighComp[k]:
            for values in dictBCF[k]:
                if values == v: #Broken
                    countHighComp += 1
                    resHighCompKey.append(k)
                    resHighCompValue.append(values)
                    resDict = dict(zip(resHighCompKey,resHighCompValue))
        wordListHighComp.append(resDict)
                
                
    for k in dictBCF.keys() & synTechComp.keys():
        resTechCompKey = []
        resTechCompValue = []
        resDict = {}
        for v in synTechComp[k]:
            for values in dictBCF[k]:
                if values == v :
                    countTechComp += 1
                    resTechCompKey.append(k)
                    resTechCompValue.append(values)
                    resDict = dict(zip(resTechCompKey,resTechCompValue))
        wordListTechComp.append(resDict)
        
    while {} in wordListHighComp:
        wordListHighComp.remove({})
        
    while {} in wordListTechComp:
        wordListTechComp.remove({})
## File write              
    
    file3 = open("/Users/nsai/Documents/Research/task1.txt","a")
    file3.write(f"High Competition and its synonmys count : {countHighComp}\n")
    file3.write(f"Synonyms of High Competition present (Depicted as (k,v) pairs): \n")
    for w in wordListHighComp:
        file3.write(f"{w}\t")
        file3.write("\n")
    file3.write(f"Technological Competiton and its synonyms count : {countTechComp}\n")
    file3.write("Synonyms of Technological Competition present (Depicted as (k,v) pairs): \n")
    for w in wordListTechComp:
        file3.write(f"{w} ")
        file3.write("\n")
    file3.write(f"file name is  : {filename}\n")
    file3.write(f"year is : {year}\n")
    file3.write("\n")
    
# Print Values
    
    print("high competition and its synonmys count : ", countHighComp)
    print("Synonyms of High Competition present :", wordListHighComp )
    print("Technological competition and its synonyms count : " , countTechComp)
    print("Synonyms of Technological Competition present :", wordListTechComp)
    print("file name is  : " , filename)
    print("year is : ",year)
    file3.close()
    file2.close()

##Loop through all directories

rootdir = "/Users/nsai/Downloads/OneDrive_1_30-04-2020/10K"

filename = ""
count = 0
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        #print os.path.join(subdir, file)
        filepath = subdir + os.sep + file
        if filepath.endswith(".html"):
            synCounter(filepath,file,subdir)
            
            
