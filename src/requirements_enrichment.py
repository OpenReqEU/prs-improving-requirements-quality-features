# -*- coding: utf-8 -*-
"""
Created on Thu Jun 07 17:31:17 2018

@author: magafurzyanova
"""
#import os
import json
#import requests
# from requirements_preprocessing import kincaid, extract_features
from requirements_preprocessing import extract_features, formal_metrics
import requirements_triplets as preproc_triplets
from SPARQLWrapper import SPARQLWrapper
from Annotation_Library import annotateSentence
from lemmatizer import Lemmatizer
from textcleaner import text_cleaner
from patternmatcher import create_regex_pattern, pattern_matcher
import requests
from output_dbpedia import get_output_dbpedia

#from IPython import embed


def dbpedia_entity_types(list_of_entities):
	
	dict_type = {}
	
	for c_entity in list_of_entities:
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		prefix = """
PREFIX        wd:  <http://www.wikidata.org/entity/>
PREFIX       wdt:  <http://www.wikidata.org/prop/direct/>
PREFIX  wikibase:  <http://wikiba.se/ontology#>
PREFIX         p:  <http://www.wikidata.org/prop/>
PREFIX        ps:  <http://www.wikidata.org/prop/statement/>
PREFIX        pq:  <http://www.wikidata.org/prop/qualifier/>
PREFIX        bd:  <http://www.bigdata.com/rdf#>
PREFIX       owl:  <http://www.w3.org/2002/07/owl#>
PREFIX      rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX      foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX       dct:  <http://purl.org/dc/terms/>
PREFIX       dbo:  <http://dbpedia.org/ontology/>
PREFIX       dbp:  <http://dbpedia.org/property/>

"""

		dbp_query = prefix + """
SELECT DISTINCT ?x ?s
{
			select ?s ?x where{
			values ?x { <http://dbpedia.org/resource/""" + c_entity + """> }
			?x dct:subject	?s.
	}
}

"""
		sparql.setQuery( dbp_query.encode("utf-8").decode("unicode_escape") )
		sparql.setReturnFormat("json")
		try:
			results = sparql.query()
			allDone = 1
			content = results.response.readlines()
			content_dict = json.loads("".join(content))
			list_of_types = [ c_el['s']['value'] for c_el in content_dict['results']['bindings'] ]
			dict_type[c_entity] = list_of_types
		except Exception as e:
			print(dbp_query)
			print "ERROR IN QUERY: " + e.message
			allDone = 0
			print("RETRYING")
			dict_type[c_entity] = []
	
	return dict_type


def lemmatizer(element,lem_obj): 
    lemmatized_list = lem_obj.lemmatize(sentences_list=[element])
    return ' '.join(lemmatized_list[0]) # element
    


def dbpedia(element,tc_obj,param_dbpedia_dict):

    uri, entities, patterns, text = get_output_dbpedia(document= element, 
                                                       tc= tc_obj, 
                                                       confidence =  param_dbpedia_dict['confidence'], 
                                                       custom_entities = [], 
                                                       dbpediaspotlight_url = param_dbpedia_dict['dbpediaspotlight_url'], 
                                                       useProxy=  param_dbpedia_dict['useProxy'])
    return entities




def enrich(element_dict, wordlist_list, verb_arguments_parser,lem_obj,tc_obj,param_dbpedia_dict):

    if 'Bullet' in element_dict.keys() or 'Paragraphs' in element_dict.keys(): 
        key = 'Bullet' if 'Bullet' in element_dict else 'Paragraphs'
        try:
            element_dict['lemmatizedContent'] = lemmatizer(element_dict[key],lem_obj)
        except:
            element_dict['lemmatizedContent'] =[]
        '''
        try:
            element_dict['dbpediaEntities'] = dbpedia(element_dict[key],tc_obj,param_dbpedia_dict) 
        except:
            element_dict['dbpediaEntities'] = []

        try:
            element_dict['dbpediaEntitiesType'] = dbpedia_entity_types(element_dict['dbpediaEntities'])
        except: 
            element_dict['dbpediaEntitiesType'] = {}
        '''        
        for i in range(len(wordlist_list)):
            element_dict['d'+str(i)] = extract_features([element_dict[key]], wordlist_list[i])[0]
         
        element_dict['entities'] = verb_arguments_parser.calculate_paragraph_structure(element_dict[key])
        if len(element_dict[key])!=0:
            element_dict['formalMetrics'] = formal_metrics(element_dict[key])
        else:
            element_dict['formalMetrics'] = dict({ 'ease': None, 'kincaid': None })        
    return element_dict
        
		
def json_to_structured_dict(input_json):
    dict_list = []
    for el in input_json:
        ret_dict = {}
        if len(el)!=0:  
            try:
                # for i in range(len(input_data)):
                # for values in zip(el['PID'],el['Paragraphs']):
                for i in range(len(el['PID'])):
                    temp_dict = {}
                    temp_dict['PID'] = el['PID'][i]
                    temp_dict['Paragraphs'] = el['Paragraphs'][i]
                    temp_dict['Line'] = el['Line']
                    try:
                        temp_dict['Title'] = el['Title']
                    except KeyError:
                        pass
                    # ret_dict = dict(zip([('PID','Paragraphs') for i in range(len(el['PID']))],zip(el['PID'], el['Paragraphs']))) 
                    # ret_dict['Line'] = el['Line']
                    dict_list.append(temp_dict)
            except KeyError:
                try:
                    ret_dict['Bullet'] = el['Bullet']
                    ret_dict['Line'] = el['Line']
                    try:
                        ret_dict['Title'] = el['Title']
                    except KeyError:
                        pass
                except KeyError:
                    pass       
    
        if len(ret_dict) != 0:
            dict_list.append(ret_dict)  
    return dict_list            

# path = 'data'
# texts = 'json_out.json'

endpoint_lemmatizer = '/lemmatizer/en'
endpoint_entities_extractor = '/keywords/supervised/en'
baseAdress = 'http://193.109.207.65:15024/nlp'
# baseAdressDBPedia = 'http://193.109.207.65:15000'
baseAdressDBPedia = 'http://127.0.0.1:5004'
endpointUrl = 'http://127.0.0.1:42001/rest/annotate'
endpointheaders = {"Accept": "application/json"}
endpoint_uke='keywords/unsupervised/regex'

