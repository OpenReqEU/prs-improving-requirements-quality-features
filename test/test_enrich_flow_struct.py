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

"""

import requests
import json
import os
import time
from IPython import embed

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



print '---------------------------'
print 'dbpedia entity types'
list_of_entities =  [u'Monodontidae', u'Physeteridae']
data = { 'listOfEntities': list_of_entities}
out = tester_app(endpoint='api_t_33/parsing/types',baseAddress=baseAddress, data=data)
print out

print ('---------------------------------------')
print "features:"
data = {'document': text}
out = tester_app(endpoint='api_t_33/parsing/features',baseAddress=baseAddress, data=data)
print out



print ('---------------------------------------')
print ("structure:")
data = { 'document': text}
out = tester_app(endpoint='api_t_33/parsing/structure',baseAddress=baseAddress, data=data)
print (out)


"""
print '---------------------------------------'
print "metrics:"
out = tester_app(endpoint='api_t_33/parsing/metrics',baseAddress=baseAddress, data=data)
print out
"""

