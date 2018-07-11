#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 16:26:24 2018

Engineering Ingegneria Informatica spa
Big Data & Analytics Competency Center

@author: francesco pareo
@location: bologna
"""

# packages
import re
# libraries
from textcleaner import text_cleaner
tc = text_cleaner(rm_punct = True, rm_tabs = True, rm_newline = True, 
                             rm_digits = False, rm_hashtags = True, rm_tags = True, 
                             rm_urls = True, tolower=False, rm_email=True, rm_html_tags = True,  
                             rm_apostrophe = True, rm_underscore = True, rm_minus = True)


def create_regex_pattern(pattern_vec,min_len = 4):
    """
    This function takes as input a vector of patterns to be searched in a text, 
    and returns a dictionary with keys = original patterns and values = corresponding compiled regexes.
    if the length of a certain pattern is greater than min_len, the function will put such pattern in lowercase.
    
    Args:
        pattern_vec (list of strings): the patterns to be transformed into compiled regexes
        min_len (int): the minimum length for a pattern to be put in lowercase
        
    Returns:
        regex_pattern_dict (dict): the dictionary containing the compiled regexes
    """
    
    regex_pattern_dict = {}
    for pattern in pattern_vec:
        p1 = pattern.replace(" ", "_")
        
        if(len(pattern)>=min_len):
            p2 = re.compile(r'\b'+re.escape(pattern.lower())+r'\b')
            p1 = p1.lower()
        else:
            p2 = re.compile(r'\b'+re.escape(pattern)+r'\b')
            
        regex_pattern_dict[p1] = p2
        
        
    return regex_pattern_dict

def pattern_matcher(text,pattern,regex_pattern):
    """
    This function takes a single sentence as input, and given a regex_pattern and its original mapping, 
    it extracts all objects corresponding to such mapping. 
    A 'normalized' text and a list of extracted patterns is then returned.
    NB:an empty list may be returned, if no matches have been found. The output text will then be equal to the input text.
    
    Args:
        text (string): the input text
        pattern (string): the pattern to be searched into the text
        regex_pattern (compiled regex object): the regex to be used to look for the pattern
        
    Returns:
        text_edit (string): the normalized text
        pattern_list (list): the patterns that have been extracted
    """
    
    # tolower text
    text_lower = text.lower()
    # new text to be updated
    text_edit = text
    # find the matches
    myMatches = regex_pattern.finditer(text_lower)
    pattern_list = []
    # find the match and update the text 
    for m in myMatches:
        text_edit = text_edit[0:m.start()] + pattern + text_edit[m.end():len(text_edit)]
        pattern_list.append(pattern)
        
    return text_edit, pattern_list
