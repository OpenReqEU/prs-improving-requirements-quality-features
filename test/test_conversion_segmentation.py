#!/usr/bin/env python2
# -*- coding: utf-8 -*-


"""
Created on 18/06/2018
Engineering Ingegneria Informatica spa
Big Data & Analytics Competency Center
@author: chiara accadia

Test of following REST SERVICE: 

1- "api_t_33/parsing/conversion/doc"
2- "api_t_33/parsing/segmentation"
3- "api_t_33/parsing/to_dict"
4- "api_t_33/parsing/enrich"
5- "api_t_33/parsing/enrich/prettify"

"""

import requests
import json
import time
import os

#%%#########################################################
################ Input data ################################  
############################################################

path1='../data/'
file_word1 = 'prova_whales.docx'
filename1 = path1+file_word1

path2='../data/processed/'
file_word2 = 'prova_whales.txt'
filename2 = path2+file_word2

baseAddress = "http://127.0.0.1:10602"

#endpoint1 =  "/api_t_33/parsing/conversion/doc"
#endpoint2 =  "/api_t_33/parsing/segmentation"
#endpoint3 =  "/api_t_33/parsing/to_dict"
#endpoint4 =  "/api_t_33/parsing/enrich"
#endpoint5 =  "/api_t_33/parsing/enrich/prettify"

endpoint1 =  "/prs-improving-requirements-quality-features/parsing/conversion/doc"
endpoint2 =  "/prs-improving-requirements-quality-features/parsing/segmentation"
endpoint3 =  "/prs-improving-requirements-quality-features/parsing/to_dict"
endpoint4 =  "/prs-improving-requirements-quality-features/parsing/enrich"
endpoint5 =  "/prs-improving-requirements-quality-features/parsing/enrich/prettify"


#%%#########################################################
################    Test    ################################  
############################################################

print('---------------------------------------')
print('conversion')
r1 = requests.post(baseAddress + endpoint1, files={'file': open(filename1,'rb')})
assert (r1.json())['error']['status'] == 600   
print(r1)


print('---------------------------------------')
print('segmentation')
dict_file = { filename2 : open(filename2, 'rb')}
data_json = {'numParagraph':15}
files = [
    ('file', (filename2, open(filename2, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data_json), 'application/json')),
]
r2 = requests.post(baseAddress + endpoint2, files= files)
assert isinstance((r2.json())['content'], list) and len((r2.json())['content']) >0 and (r2.json())['error']['status'] == 600   
print(r2)


print('---------------------------------------')
print('structured dictionary')
data = r2.json()['content'] 
r3 = requests.post(baseAddress + endpoint3, data= json.dumps({"listOfBlocks" : data }), headers={"Content-Type": 'application/json'})
assert isinstance((r3.json())["content"], list) and len((r3.json())["content"]) != 0 and  (r3.json())['error']['status'] == 600   
print(r3)
print(r3)


print('---------------------------------------')
print('enriched dictionary')
data = r3.json()['content'] 
r4 = requests.post(baseAddress + endpoint4, data= json.dumps({"structuredDictList" : data }), headers={"Content-Type": 'application/json'})
assert isinstance((r4.json())['content'], list) and len((r4.json())['content']) != 0 and (r4.json())['error']['status'] == 600   
print(r4)

print('---------------------------------------')
print('print pretty enriched dictionary')  
data = r4.json()['content'] 
r5 = requests.post(baseAddress + endpoint5, data= json.dumps({"enrichedDictList" : data }), headers={"Content-Type": 'application/json'})
assert isinstance(r5.json()['content'], list) and len(r5.json()['content']) != 0 and r5.json()['error']['status'] == 600
print(r5)   
