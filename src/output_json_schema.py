# -*- coding: utf-8 -*- 

from codecs import open
import os
import time
import json





#params
path = './json_mapping_test_data' 
real_json = 'json_input_file_prova.json'

json_output_fields = ['requirement', 'requirementParts']
json_output_additional_fields = ['attachment', 'comment', 'dependency', 'required', 'classifier', 'project', 'release', 'person', 'participant', 'responsible']


          
def extract_fields_from_input_dict(inner_dict):    
    '''extracts info from enriched dictionary and saves it in a tuple'''    
    
    #create requirementParts list of dictionaries
    list_of_dictionaries = []
    
    #inner dictionary for requirementPart field
    required_keys = ['d0', 'd1', 'd2', 'd3', 'dbpediaEntities', 'dbpediaEntitiesType']
    
    textual_keys = ['lemmatizedContent', 'formalMetrics', 'Title', 'Paragraphs']
      
    
    
    for el in required_keys:
        property_dictionary = {}
        
        try:
            identifier = inner_dict['Line'] + '_' + inner_dict['PID']
            property_dictionary['id'] = identifier
        except KeyError:
            identifier = inner_dict['Line'] + '_' + 'P1'
            property_dictionary['id'] = identifier
        
        property_dictionary['name'] = el
        try:
            property_dictionary['content'] = inner_dict[el]
        except KeyError:
            property_dictionary['content'] = inner_dict[el]

        property_dictionary['created_at'] = int(time.time())
        list_of_dictionaries.append(property_dictionary)
    
    entities_dictionary = {}
    try:
        identifier = inner_dict['Line'] + '_' + inner_dict['PID']
        entities_dictionary['id'] = identifier
    except KeyError:
        identifier = inner_dict['Line'] + '_' + 'P1'
        entities_dictionary['id'] = identifier
    
    entities_dictionary['name'] = 'structure'
    entities_dictionary['content'] = inner_dict['entities']
    
    entities_dictionary['created_at'] = int(time.time())    
    list_of_dictionaries.append(entities_dictionary)         
            
    for el in textual_keys:
        property_dictionary = {}

        try:
            identifier = inner_dict['Line'] + '_' + inner_dict['PID']
            property_dictionary['id'] = identifier
        except KeyError:
            identifier = inner_dict['Line'] + '_' + 'P1'
            property_dictionary['id'] = identifier  
        
        property_dictionary['name'] = el
        try:
            property_dictionary['text'] = inner_dict[el]
        except KeyError:
            property_dictionary['text'] = inner_dict[el]
     
        property_dictionary['created_at'] = int(time.time()) 
        list_of_dictionaries.append(property_dictionary)
        
    return list_of_dictionaries   
        
        
        
def generate_json_schema(inner_dict):
    '''Main function. It creates a new dictionary, fills it with information 
       and uses the tuple with info from enriched dictionary to fill the new dictionary. 
       The output is a new python dictionary with 'requirements' and 'requirementsParts' keys'''
    

    
    #create json and data structures
    json_output = {}
    
    #define json main fields
    json_fields = json_output_fields
    json_additional_fields = json_output_additional_fields
    
    
    #create dictionary with main fields
    for key in json_fields:
        json_output[key] = {}
    
    
    #fill each field    
    
    #extract requirementsParts field information
    requirementspart = extract_fields_from_input_dict(inner_dict)

    if 'Line' in inner_dict.keys() and 'PID' in inner_dict.keys():    

        #fill requirement 'id' and 'created_at' fields
        try:
            identifier = inner_dict['Line'] + '_' + inner_dict['PID']
            json_output['requirement']['id'] = identifier
        except KeyError:
            identifier = inner_dict['Line'] + '_' + 'P1'
            json_output['requirement']['id'] = identifier
        
  
        json_output['requirement']['created_at'] = int(time.time())     

        #fill requirementsParts field
        json_output['requirementParts'] = requirementspart
    
    return json_output

    
    
def map_enriched_dictionary_to_json_schema(path, json_input):  
    '''Orchestrator function. It opens the input json file, it opens a new json and writes the new json structure''' 
    
    
    input_dictionary_list = []
    json_schema = []
    with open(os.path.join(path, json_input), 'rb', encoding='utf-8') as input_file:
        input_dictionary_list = json.load(input_file)

    for inner_dict in input_dictionary_list:
        json_enriched = generate_json_schema(inner_dict)
        json_schema.append(json_enriched)
    
    #with open(os.path.join(path, 'json_schema.json'), 'wb', encoding='utf-8') as output_schema:         
    #    json_dictionary_complete = json.dump(json_schema, output_schema,  ensure_ascii=False, indent=4, encoding='utf-8')
            
           
           
if __name__ == '__main__':
    prova = map_enriched_dictionary_to_json_schema(path, real_json)

