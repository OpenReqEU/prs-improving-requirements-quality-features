# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 18:06:34 2018

@author: magafurzyanova,micgabus
"""

# from textstat.textstat import textstatistics
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from textstat import textstatistics

def extract_features(paragraph, wordlist): 
    wordlist = list(set([ word.strip() for word in wordlist]))
    object_extractor = CountVectorizer(paragraph, ngram_range = (1,4),vocabulary=wordlist) 
    feature_extractor = object_extractor.fit_transform(paragraph) 
    features_dictionary = pd.DataFrame(feature_extractor.toarray(), columns=object_extractor.get_feature_names()).to_dict('records')
    return features_dictionary

def formal_metrics(my_text):  
	a = textstatistics()
        try:
	    ease =  a.flesch_reading_ease(my_text)
	except TypeError:
            ease = ''
        
        try:
            kincaid = a.flesch_kincaid_grade(my_text)
	except TypeError:
            kincaid = ''
    
        return dict({ 'ease':ease, 'kincaid':kincaid })
