#!/usr/bin/env python2
# -*- coding: utf-8 -*-


"""
Created on 18/06/2018
Engineering Ingegneria Informatica spa
Big Data & Analytics Competency Center
@author: chiara accadia

Test of following REST SERVICE: 
                 
1- "api_t_33/parsing/lemmatizer/en"
2- 'api_t_33/parsing/keywords/supervised/en'
3- 'api_t_33/parsing/types'
4- 'api_t_33/parsing/features'
5- 'api_t_33/parsing/structure'
6- 'api_t_33/parsing/metrics'
7- 'api_t_33/parsing/enrich'
8- 'api_t_33/parsing/enrich/prettify'

"""

import requests
import json
import os
import time


def tester_app(endpoint, baseAddress, data):
	t = time.time()
	req = requests.post(os.path.join(baseAddress,endpoint), data=json.dumps(data))
	print("ELAPSED: " + str(time.time() - t))
	resp = req.json()
	return resp

#%%#########################################################
################ Input data ################################  
############################################################

#rest service address
baseAddress = "http://127.0.0.1:10602/" # LOCAL MN03 app


document_en =[ u"the girls went from Mars.", 
           u"He eats a lot of potatoes"]


text = """Whales are a widely distributed and diverse group of fully aquatic placental marine mammals. They are an informal grouping within the infraorder Cetacea, usually excluding dolphins and porpoises. Whales, dolphins and porpoises belong to the order Cetartiodactyla with even-toed ungulates and their closest living relatives are the hippopotamuses, having diverged about 40 million years ago. The two parvorders of whales, baleen whales (Mysticeti) and toothed whales (Odontoceti), are thought to have split apart around 34 million years ago. The whales comprise eight extant families: Balaenopteridae (the rorquals), Balaenidae (right whales), Cetotheriidae (the pygmy right whale), Eschrichtiidae (the grey whale), Monodontidae (belugas and narwhals), Physeteridae (the sperm whale), Kogiidae (the dwarf and pygmy sperm whale), and Ziphiidae (the beaked whales)."""


print ('---------------------------')
print ('Text:')
print (text )


print ('---------------------------')
print ('lemmatizer')
data = {'documents' : [text]}
out = tester_app(endpoint='api_t_33/parsing/lemmatizer/en',baseAddress=baseAddress, data=data)

assert out['content']['lemmatizedDocuments'] != [] 
print(out)


print ('---------------------------')
print ('dbpedia entities')
data = {'document' : text}
out = tester_app(endpoint='api_t_33/parsing/keywords/supervised/en',baseAddress=baseAddress, data=data)

assert isinstance(out['content'], dict)
assert 'dbpediaUri' and 'dbpediaEntities' in out['content'].keys()
assert (len(out['content']['dbpediaUri']) == len(out['content']['dbpediaEntities']))
assert out['content']['normalizedDocument'] != u''

assert out['error']['status'] == 600    

print(out)



print ('---------------------------')
print ('dbpedia entity types')
list_of_entities =  [u'Monodontidae', u'Physeteridae']
data = { 'listOfEntities': list_of_entities}
out = tester_app(endpoint='api_t_33/parsing/types',baseAddress=baseAddress, data=data)
assert isinstance(out['content'], dict)
assert len(out['content']['typeDict'].keys()) == len(list_of_entities)

assert out['error']['status'] == 600 
print (out)





print ('---------------------------------------')
print ("features:")
data = {'document': text}
out = tester_app(endpoint='api_t_33/parsing/features',baseAddress=baseAddress, data=data)
expected_out = {'featuresDict' : {u'will be': 0, u'is planned': 0, u'is envisaged': 0, u"it's planned": 0, u"it's foreseen": 0, u'is foreseen': 0, u'following': 0}, u'error': {u'status': 600, u'code': u'OK', u'description': u'Application run normally.'}}
if isinstance(out['content'], dict): 
    assert isinstance(out['content'], dict) == isinstance(expected_out['featuresDict'], dict) 
    assert len(out['content']['featuresDict']) ==  len(expected_out['featuresDict']) 
else:
    raise Exception

assert out['error']['status'] == 600    

print (out)




print ('---------------------------------------')
print ("structure:")
data = { 'document': text}
out = tester_app(endpoint='api_t_33/parsing/structure',baseAddress=baseAddress, data=data)

expected_data = {'paragraphDict' : [
   {u'adjectives': [],
    u'dependence': [],
    u'hash_number': 13657967055247313476,
    u'lemmatized_verb': u'comprise',
    u'objects': u'families',
    u'objects_extended': [u'eight extant families'],
    u'subjects': [u'whales'],
    u'subjects_extended': [u'The whales Balaenopteridae ( the rorquals ) , Balaenidae ( right whales ) , Cetotheriidae ( the pygmy right whale ) , Eschrichtiidae ( the grey whale ) , Monodontidae ( belugas and narwhals ) , Physeteridae ( the sperm whale ) , Kogiidae ( the dwarf and pygmy sperm whale ) , and Ziphiidae ( the beaked whales )'],
    u'verbs': u'comprise'}]
    }
assert isinstance(out['content']['paragraphDict'], list) == isinstance(expected_data['paragraphDict'], list) and out['content']['paragraphDict'] != [] 

assert out['error']['status'] == 600    

print (out)



print ('---------------------------------------')
print ("metrics:")
out = tester_app(endpoint='api_t_33/parsing/metrics',baseAddress=baseAddress, data=data)

assert isinstance(out['content']['dictMetrics'], dict) and len(out['content']['dictMetrics']) == 2

assert out['error']['status'] == 600  

print(out)




