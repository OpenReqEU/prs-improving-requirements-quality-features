#!/usr/bin/env python2
# -*- coding: utf-8 -*-


"""
Created on 18/06/2018
Engineering Ingegneria Informatica spa
Big Data & Analytics Competency Center
@author: chiara accadia

Test of following REST SERVICE: 

"/'api_t_33/uploader"

"""

import requests
import json
import time
import os



#%%#########################################################
################ Input data ################################  
############################################################
endpoint =  "http://127.0.0.1:10602/api_t_33/uploader"

path='../data/'
file_word = 'example_tender1_confidential.docx'
#file_word = 'test.pdf'
filename = path+file_word

data = {'numParagraph':15}

#%%#########################################################
################    Test    ################################  
############################################################

 
#files = {'json': (None, json.dumps(data), 'application/json'),'file': (filename2, open(filename2, 'rb'), 'application/octet-stream')}


files = [
    ('file', (filename, open(filename, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data), 'application/json'))
]

#%%#########################################################
################    Test    ################################  
############################################################

#response = requests.post(endpoint, files={'file': open(filename,'rb')})
response = requests.post(endpoint, files=files)
print(response.content)
                 
