# -*- coding: UTF-8 -*-

"""
Engineering Ingegneria Informatica spa
Big Data & Analytics Competency Center

@author:  matteo sartori, francesco pareo
@location: Bologna
"""

import re
import urlparse
import os
import requests
from requests.auth import HTTPProxyAuth
import json
from itertools import chain



#%% extract DBPedia resources from JSON

def extractDbpediaresources(responseAsJson):
    """
    This function takes a JSON as input and returns a list containing, for each element, a list of dbpedia resources (entity,URI,etc.).
    Such JSON is the result of a DBPedia API call of a single text.
    
    Args:
        responseAsJson (string): The input JSON
        
    Returns:
        list (undefined length) of 4-elements lists (URI,surfaceForm,types,offset)
        NB: may return an empty list
    """
    
    resources = []
    if 'Resources' in responseAsJson.keys():
        for resource in responseAsJson['Resources']:
                resources.append([resource['@URI'], resource['@surfaceForm'], resource['@types'], resource['@offset']])
    return resources




#%% entitized text function

def updateResources(sentence,resources):
    
    """
    This function takes as input the original text and the resources extracted by DBPedia API, and returns 
    two lists containing DBPedia extracted entities and URIs. The 'entitized' text is also returned.
    If an empty list is provided, the output text will be equal to the original text and two empty lists will be returned.
    NB: in the 'entitized' text, each original object recognized by DBPedia must be replaced by its corresponding DBPedia entity
    
    Args:
        sentence (string): the original sentence
        resources (list): the resources extracted by DBPedia API
        
    Returns:
        updatedEntity (list): the DBPedia entities extracted by the API
        updatedURI (list): the DBPedia URIs extracted by the API
        entitizedSentence (string): the 'entitized' text
    """
    
    # initialize objects
    updatedEntity = []
    updatedUri = []
    entitizedSentence = sentence
    currentOffset = 0
    
    
    # for each extracted resource:
    for resource in resources:
        
        # surface (unused at the moment)
        surfaceForm = resource[1]
        
        # process the uri
        uri = resource[0]
        uri = re.sub(string = uri, pattern = ur',', repl = "")
        updatedUri.append([uri])
        
        # extract the entity from the URI
        entity = resource[0]
        try:
            entity = re.search(pattern = r'(/resource/)(.+)$',string = entity).group(2)
        except AttributeError:
            entity = 'ERROR'
        updatedEntity.append([entity])

        # entitized sentence (each original object must be replaced by its corresponding DBPedia entity)
        startingPoint = int(resource[3])
        entitizedSentence = entitizedSentence[0:(startingPoint+currentOffset)]+entity+entitizedSentence[(startingPoint+len(resource[1])+currentOffset):len(entitizedSentence)]
        currentOffset = currentOffset + len(entity)-len(resource[1])
        
    return updatedEntity, entitizedSentence, updatedUri


#%% DBPedia annotation main function

def annotateSentence(sentence, dbpediaspotlight_url, language='en', useProxy = False, confidence = 0.6):
    
    """
    This function takes the original text as input and sends it to the DBPedia API, by specifying the extraction confidence.
    Returns the 'entitized' text and the lists containing the extracted entities and URIs.
    Such lists may be empty, and the output text may be equal to the input text.
    
     Args:
        sentence (string): the original sentence
        useProxy (bool): whether the proxy should be used
        confidence (float): the extraction confidence for DBPedia REST service, range = ]0,1[ , default = 0.6
        
    Returns:
        out_uri (list): list of URIs
        out_entities (list): list of URIs
        out_text (string): 'entitized' text
        sentence (string): original text
    """
    
    
    # REST service configuration parameters
    endpointUrl = dbpediaspotlight_url # re.sub("\{\}", language, DBPEDIASPOTLIGHT_URL)
    endpointheaders = {"Accept": "application/json", 'Content-Type':'application/x-www-form-urlencoded'}
    proxies = None
    auth = None
    body = {}
    if (useProxy):
        if not (os.environ['http_proxy']):
                raise Exception("use proxy specified but http_proxy variable not present")
        else:
            proxyUrl = urlparse.urlparse(os.environ['http_proxy'])
            proxies = {'http': proxyUrl.hostname + ":" + str(proxyUrl.port)}
            auth = HTTPProxyAuth(proxyUrl.username, proxyUrl.password) 
            
    
    # check if the input text is valid. if it is not a string, exit the function and return empty lists and empty text
    if(type(sentence)==float): 
        #print 'warning: could not annotate this sentence'
        out_uri = []
        out_entities = []
        out_text = ''
        
    # otherwise, apply REST service
    else:
        body = {}
        body['text'] = sentence
        body['confidence'] = confidence
        response = requests.post(endpointUrl, headers=endpointheaders, data=body)
        # the service failed:
        if( response.status_code != 200 ):
            #print 'warning: could not annotate this sentence'
            out_uri = []
            out_entities = []
            out_text = ''
        # if the service succeded:
        else:
            responseAsJson = json.loads(response.content.decode('utf-8'))
            resources = extractDbpediaresources(responseAsJson)
            out_entities, out_text, out_uri = updateResources(sentence,resources)
            out_entities = list(chain(*out_entities))
            out_uri = list(chain(*out_uri))
            
    # return objects
    return out_uri, out_entities, out_text, sentence
    


