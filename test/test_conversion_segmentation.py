#!/usr/bin/env python2
# -*- coding: utf-8 -*-


"""
Created on 18/06/2018
Engineering Ingegneria Informatica spa
Big Data & Analytics Competency Center
@author: chiara accadia

Test of following REST SERVICE: 

"api_t_33/parsing/conversion/doc"
"api_t_33/parsing/segmentation"

"""

import requests
import json
import time
import os



#%%#########################################################
################ Input data ################################  
############################################################

path1='../data/'
file_word1 = 'EVOLUTION.DOCX'
filename1 = path1+file_word1

#path2 = '../output/'
path2='../data/processed/'
file_word2 = 'EVOLUTION.txt'
filename2 = path2+file_word2



endpoint1 =  "http://127.0.0.1:10602/api_t_33/parsing/conversion/doc"
endpoint2 =  "http://127.0.0.1:10602/api_t_33/parsing/segmentation"



data = {'numParagraph':15}

#%%#########################################################
################    Test    ################################  
############################################################

 
#files = {'json': (None, json.dumps(data), 'application/json'),'file': (filename2, open(filename2, 'rb'), 'application/octet-stream')}


files = [
    ('file', (filename2, open(filename2, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data), 'application/json')),
]

print 'conversion'
r1 = requests.post(endpoint1, files={'file': open(filename1,'rb')})
print r1

print 'segmentation'
#r2 = requests.post(endpoint2, files={'file': open(filename2,'rb')})
r2 = requests.post(endpoint2, files=files)
print r2.content

                     
  
