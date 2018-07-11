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
baseAddress = "http://127.0.0.1:5007/" # LOCAL MN03 app


document_en =[ u"the girls went from Mars.", 
           u"He eats a lot of potatoes"]


text = """For the purposes of works performance in the area with traffic flow, the continuous 8-hour closings of the railway line (principally from 715 am to 1515 pm 	each working day) shall be set up. Exceptionally, depending on the technology and the demands of the specific works performance, the closings of the railway line lasting 12/24/48/72 hours (principally on weekends from  Friday to Monday) shall be approved. Performance of works  in the area with traffic flow  is necessary only in railway line sections which cannot measure more than 5 kilometres, and it can be executed only in one such section at the time."""


print '---------------------------'
print 'Text:'
print text 


#%%#########################################################
################     Test   ################################  
############################################################

print '---------------------------'
print 'Lemmatizer'
data = { 'documents' :[text]}
# optional  params
data['selectedPOS'] =  ['J','V', 'N', 'R']
data['removeStopwords'] = [u'from', u'the']
out = tester_app(endpoint='api_t_33/parsing/lemmatizer/en', baseAddress=baseAddress, data=data)
print out




print '---------------------------'
print 'dbpedia'
my_data = {'document': text}
#optional parameters
my_data['confidence']=0.6
#my_data['customEntities']=['Achilles','rather','along','pippo']
out_en = tester_app(endpoint = 'api_t_33/parsing/keywords/supervised/en', baseAddress = baseAddress, data=my_data)
print out_en



print '---------------------------'
print 'dbpedia entity types'
list_of_entities =  [u'Koprivnica', u'Distances']
data = { 'listOfEntities': list_of_entities}
out = tester_app(endpoint='api_t_33/parsing/types',baseAddress=baseAddress, data=data)
print out



print '---------------------------------------'
print "features:"
data = {'document': text}
out = tester_app(endpoint='api_t_33/parsing/features',baseAddress=baseAddress, data=data)
print out



print '---------------------------------------'
print "structure:"
data = { 'document': text}
out = tester_app(endpoint='api_t_33/parsing/structure',baseAddress=baseAddress, data=data)
print out



print '---------------------------------------'
print "metrics:"
out = tester_app(endpoint='api_t_33/parsing/metrics',baseAddress=baseAddress, data=data)
print out


