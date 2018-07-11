# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 10:31:17 2018

@author: chaccadi
"""

import json
from Annotation_Library import annotateSentence 
from patternmatcher import create_regex_pattern

 

def get_output_dbpedia(document, tc, confidence, custom_entities, dbpediaspotlight_url, useProxy):
 

    """
    This functions get entities of dbpedia spotlight. 
    
    Args:
        document: (string) text
        tc: object of textclener 
        confidence: dbpedia confidence extraction
        custom_entities: list of user entities 
        dbpediaspotlight_url: url for italian or english language
        useProxy: True or False

        
    Returns:
       uri: list of uri
       entities: list of entities
       patterns: list of pattern matching
       text: text with entities
    
    """   
    
    # cleaning text
    document = tc.regex_applier(document)
    
    # dbpedia-spotlight 
    uri, entities, text, _ = annotateSentence(sentence=document, 
                                              dbpediaspotlight_url= dbpediaspotlight_url,
                                              useProxy = useProxy,
                                              confidence = confidence)
   
    # extract custom entities and check its validity
    patterns = []
    if isinstance(custom_entities,list) and len(custom_entities)!=0:
        regexes = create_regex_pattern(pattern_vec=custom_entities,min_len = config_parameters['ske']['pm_lower_min_len'])
        for k, v in regexes.iteritems():
            text, pattern = pattern_matcher(text=document,pattern=k,regex_pattern=v)
            patterns.append((k,len(pattern)))
      
 
    return  uri, entities, patterns, text 
       

