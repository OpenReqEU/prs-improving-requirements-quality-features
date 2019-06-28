# -*- coding: utf-8 -*-
"""
Created on Wed May 30 09:28:36 2018
"""
import json
from flask import Flask, jsonify, request
#from flask_swagger import swagger
from flasgger import Swagger
from flask_cors import CORS
# import requirements_preprocessing as preproc_mod
import src.requirements_segmentation as preproc_seg
import src.requirements_enrichment as preproc_enrich
import src.requirements_triplets as preproc_triplets
from src.requirements_preprocessing import formal_metrics, extract_features
from src.lemmatizer import Lemmatizer
from src.textcleaner import text_cleaner
from src.patternmatcher import pattern_matcher
from src.output_json_schema import generate_json_schema
from src.output_dbpedia import get_output_dbpedia
import tika
from tika import parser
import requests
import time
import os
import os.path
import traceback
import sys
#from IPython import embed
#from werkzeug.utils import secure_filename
app = Flask(__name__)
swagger = Swagger(app)
cors = CORS(app)


Swagger.DEFAULT_CONFIG = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/prs-improving-requirements-quality-features/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/prs-improving-requirements-quality-features/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/prs-improving-requirements-quality-features/apidocs/"
}


@app.before_first_request
def load_data():

    global baseAddress 
    #global baseAdressDBPedia
    global wordFileName
    
    global config_parameters 
    with open("config/config.json") as f:
        config_parameters = json.load(f)
	
    baseAddress = config_parameters["baseAddress"]
    wordFileName = config_parameters["dummyInput"]["docFile"]
    
    global fileWord
    fileWord = open(wordFileName, 'w')
    
    global verb_arguments_parser
    verb_arguments_parser = preproc_triplets.EnglishPredicateArguments(config_parameters["spacyModels"]["en"])
    
    global wordlist_list
    wordlist_list = []
 
    with open(config_parameters["dictionaries"]["avg_scores"]) as av_scores_text:
        average_scores_raw = av_scores_text.read()
    average_scores = average_scores_raw.split('\r\n')
    wordlist_list.append(average_scores)

    with open(config_parameters["dictionaries"]["sections"]) as dict_sect_text:
        dict_sect_raw = dict_sect_text.read()
    dict_sect = dict_sect_raw.split('\n')
    wordlist_list.append(dict_sect)
    
    print("Loading scores...")
    with open(config_parameters["dictionaries"]["high_scores"]) as high_scores_text:
        high_scores_raw = high_scores_text.read()
    high_scores = high_scores_raw.split('\r\n') 
    wordlist_list.append(high_scores)

    with open(config_parameters["dictionaries"]["low_scores"]) as low_scores_text:
        low_scores_raw = low_scores_text.read()
    low_scores = low_scores_raw.split('\r\n')   
    wordlist_list.append(low_scores)
    global server_errors
    server_errors = json.load(open(config_parameters["internals"]["errors"],'r'))

    #lemmatizer 
    print("Loading lemmatizer...")
    global lem
    lem = Lemmatizer(lang='en', 
                     fast=config_parameters['lemmatizer']['fast'],
                     proxy_setup=config_parameters['lemmatizer']['proxy_setup'],
                     chunk_size=config_parameters['lemmatizer']['chunk_size'],
                     service_address =config_parameters['lemmatizer']['service_address'],
                     stopwords_list=None,
                     pos_list=None)
    lem.load_morphit_dict(dict_filename=config_parameters['lemmatizer']['morphit_dict'], decoder_POS_file=config_parameters['lemmatizer']['decoder_pos'])

    #textcleaner
    global tc
    tc = text_cleaner(rm_punct = True, rm_tabs = True, rm_newline = True, rm_digits = False,
                  rm_hashtags = True, rm_tags = True, rm_urls = True, tolower=False,
                  rm_email=True, rm_html_tags = True) 





###########################
#####  Orchestrator #######
###########################
@app.route('/prs-improving-requirements-quality-features/uploader/<num_par>', methods = ['GET','POST'])
def upload_file_by_name(num_par):
    
    """
        Upload a file, return enriched dict of blocks.
        ---
        consumes:
          - multipart/form-data
        produces:
          - application/json
        parameters:
          - in: formData
            name: file
            type: file
            description: The file to upload.
            required: true      
          - in: path
            name: num_par 
            type: number
            required: true
            description: Number of paragraph
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: array
                  items:
                    type: object                       
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
   
    #input file
    path = os.getcwd()+'/output/'
    if request.method == 'POST':
        try:
            f = request.files['file']       
            head, tail = os.path.split(f.filename)
            complex_name = str(time.time())+tail
            f.save(path+complex_name)
        except:
            return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}      
   
        
	if len(num_par)==0: 
            num_paragraph = config_parameters['numParsedBlocks']
        else:
            num_paragraph = num_par

        
        data = {'documentName':path+complex_name, 'numParagraph': int(num_paragraph)}
     
	  

        output = start_process(data)
        prettify_enriched_paragraphs = json.loads(output[0]).get('content')
     
	#remove files 
        try:   
            os.remove(path+complex_name)     
        except OSError:
            print ("Error: file txt not found")  
  

    elif request.method =='GET':
       prettify_enriched_paragraphs = {}

    return json.dumps({'content': prettify_enriched_paragraphs, 'error': server_errors["600"] }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    #return json.dumps({'content': {'enrichedParagraphs':enriched_paragraphs}, 'error': server_errors["600"] }), 200, {'Content-Type': 'application/json; charset=utf-8'}





def start_process(content = None):
    """
        Get a document name, return enriched dict of blocks.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                documentName:
                  type: string
                numParagraph:
                  type: integer 
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: array
                  items:
                    type: object                     
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                                    
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
    path = os.getcwd()+'/'+ config_parameters['directories']['outputDir'] + '/'  
    # input json    
    json_input = None
    if content is None:
        json_input = request.get_json(force=True)
    else:
        json_input = content	

    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    # input documentName
    file_word = json_input.get('documentName',None)
    # check validity 
    if isinstance(file_word,basestring) == False or len(file_word)==0 :
        return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}
    
    
    # paragraph number
    num_paragraph = json_input.get('numParagraph',config_parameters['numParsedBlocks'])
    # check validity
    if isinstance(num_paragraph,int) == False:
        return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}
    
    #although each service is available as microservices, we internally call them as function
    #step 1
    out_1 = convert_document(file_word)
    
    #step 2 
    head, tail = os.path.split(file_word)
    file_txt = path + "/"+ tail +'.txt'
    data = {'numParagraph' : num_paragraph}

    #files = [('file', (file_txt, open(file_txt, 'rb'), 'application/octet')),
    #         ('data', ('data', json.dumps(data), 'application/json'))]
    #out_2 = requests.post(baseAddress + "/parsing/segmentation", files=files)
    
    out_2 = None
    #out_2 = requests.post(baseAddress + "/parsing/segmentation", files=files)
    out_2 = text_segmentation(json.loads(out_1[0])["content"], data)
    list_of_blocks = json.loads(out_2[0]).get('content')
    
    #step 3
    # #transform json into structured_dict:
    data = {'listOfBlocks':list_of_blocks}
    #out_3 = requests.post(baseAddress + '/parsing/to_dict', data=json.dumps(data))
    out_3 = json_to_dict(data)
    structured_dict = json.loads(out_3[0]).get('content')
        
    # step 4
    # #enrich json (technically enrich a dict obtained from json )  
    data = {'structuredDictList': structured_dict}
    #out_4 = requests.post(baseAddress + "/parsing/enrich", data=json.dumps(data))
    out_4 = enricher(data)
    enriched_paragraphs = json.loads(out_4[0]).get('content')
        
    # step 5
    #prettify enched dict    
    data = {'enrichedDictList': enriched_paragraphs}
    #out_5 = requests.post(baseAddress + "/parsing/enrich/prettify", data=json.dumps(data))
    out_5 = get_output_json(data)
    prettify_enriched_paragraphs = json.loads(out_5[0]).get('content')


    return json.dumps({'content': prettify_enriched_paragraphs, 'error': server_errors["600"] }), 200, {'Content-Type': 'application/json; charset=utf-8'}



################################################
######## parsing and convert doc  ##############
################################################

### Step 1
@app.route('/prs-improving-requirements-quality-features/parsing/conversion/doc', methods=['POST']) 
def convert_document(filename = None):
	
    """
        Parse document with tika
        Get a document name, return parsed text.
        ---
        consumes:
          - multipart/form-data
        produces:
          - application/json
        parameters:
          - in: formData
            name: upfile
            type: file
            description: The file to upload.
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: string                   
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """

    path = os.getcwd()+'/'+ config_parameters['directories']['outputDir'] + '/'    
    if filename is None:
        f = request.files['file']
        f.save(path+f.filename)
    #parse with tika  
    try:
        if filename is None:
            parsed = parser.from_file(path+f.filename)      
        else:
            parsed = parser.from_file(filename) 
    except Exception, e: 
        return json.dumps({'content': 'PARSING ERROR', 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 

    #parsed text       
    output = parsed["content"]
    print output

    #remove uploaded docx file 
    if filename is None:
		try:
			os.remove(path+f.filename)
		except OSError:
			print ("Error while removing temporary docx file")   

    #output
    return json.dumps({'content':output, 'error' : server_errors['600'] }), 200, {'Content-Type': 'application/json; charset=utf-8'} 


### Step 2
@app.route('/prs-improving-requirements-quality-features/parsing/segmentation', methods=['POST']) 
def text_segmentation(content = None, data = None):

    
    """
        Text Segmentation
        Get a document name, return segmented text.
        ---
        consumes:
          - multipart/form-data
        produces:
          - application/json
        parameters:
          - in: formData
            name: file
            type: file
            description: The file to upload.
            required: true   
          - in: formData
            name: numParagraph
            type: object
            properties:
              numParagraph: 
                type: integer 
            description: Number of paragraphs
            required: true          
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: array
                  items:
                    type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """  
    #path = os.getcwd()+'/output/'
    path = os.getcwd()+'/'+ config_parameters['directories']['outputDir'] + '/'
    
    input_json = None
    num_paragraph = None
    if (content == None):
        f = request.files['file']
        try:         
            param_json = request.files["data"]
            f = request.files['file']
            input_json = f.read()
            num_paragraph = json.load(param_json)["numParagraph"]
        except:
            num_paragraph = config_parameters['numParsedBlocks']
    else:
            input_json = content
            try:
                num_paragraph = data.get('numParagraph')
            except:
                num_paragraph = config_parameters['numParsedBlocks']
	
    #apply segmentation
    #try:
    paragraph_list =preproc_seg.parse([el for el in input_json.replace("\n\n", "\n").split("\n") if el != ""])
    #except:
    #return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}

    #cut list 
    #num_paragraph = 15
    paragraph_out_list = []
    if len(paragraph_list) < num_paragraph:
        paragraph_out_list = paragraph_list
    else:
        paragraph_out_list = paragraph_list[0:num_paragraph]

    #output
    status = 600
    error = server_errors[str(status)]
    output = json.dumps({'content': paragraph_out_list, 'error' : error })
    if status <700:
        REST_STATUS = 200
    else:
        REST_STATUS = 500
    return output, REST_STATUS, {'Content-Type': 'application/json; charset=utf-8'}  
 

### Step 3   
@app.route('/prs-improving-requirements-quality-features/parsing/to_dict', methods=['POST'])    
def json_to_dict(content = None):

    """
        From json to a structered dict.
        Get a a list of blocks, return list of structered dict.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                listOfBlocks:
                  type: array
                  items:
                    type: object
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: array
                  items:
                    type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
    
   
    
   

    # per strutturare il file del tipo 'json_out.json' in un dizionario che terremo ed eventualmente arrichirremo
    json_input = None
    if content is None:
        json_input = request.get_json(force=True)
    else:
        json_input = content
   
    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    # check validity of input document
    list_of_blocks = json_input.get('listOfBlocks')
    if isinstance(list_of_blocks,list)==False:
         return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
   
    try:
        structured_dict = preproc_enrich.json_to_structured_dict(list_of_blocks)
    except:
        return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
   
        

    status = 600
    error = server_errors[str(status)]
    output = json.dumps({'content': structured_dict, 'error' : error })
    if status <700:
        REST_STATUS = 200
    else:
        REST_STATUS = 500
   
    return output, REST_STATUS, {'Content-Type': 'application/json; charset=utf-8'}  
 

### Step 4
@app.route("/prs-improving-requirements-quality-features/parsing/enrich", methods=['POST'])
def enricher(content = None):
   
    """
        Enricher.
        Get a text, return an enriched dict.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                structuredDictList:
                  type: array   
                  items:
                    type: object              
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: array
                  items: 
                    type: object             
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                                    
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
   
   
   

    

    param_dbpedia_dict = {}
    param_dbpedia_dict['dbpediaspotlight_url'] = config_parameters['ske']['dbpediaspotlight_url_en']
    param_dbpedia_dict['useProxy'] = config_parameters['ske']['use_proxy']
    param_dbpedia_dict['confidence'] = 0.4

    json_input = None       
    if content is None:
        json_input = request.get_json(force=True)
    else:
        json_input = content
    
    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    # check validity of input document
    structured_dict_list = json_input.get('structuredDictList',None)
    if isinstance(structured_dict_list,list)==False:
         return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 

    enriched_dicts_list = []

    try:
        for paragraph_dict in structured_dict_list:
            paragraph_dict = preproc_enrich.enrich(paragraph_dict, wordlist_list, verb_arguments_parser,lem,tc,param_dbpedia_dict)
            enriched_dicts_list.append(paragraph_dict)
    except:
        return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 

    status = 600
    error = server_errors[str(status)]
    
    output = json.dumps({'content': enriched_dicts_list, 'error' : error })
    if status <700:
        REST_STATUS = 200
    else:
        REST_STATUS = 500    
        
    return output, REST_STATUS, {'Content-Type': 'application/json; charset=utf-8'}        


### Step 5
@app.route('/prs-improving-requirements-quality-features/parsing/enrich/prettify', methods=['POST'])      
def get_output_json(content = None):


    """
        Prettify enriched dict
        Get a list of enriched dict, return a list of pretty enriched dict.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                enrichedDictList:
                  type: array
                  items: 
                    type: object 
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: array
                  items: 
                    type: object                               
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                                    
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
   
   
    
    json_schema = []
    
    json_input = None       
    if content is None:
        json_input = request.get_json(force=True)
    else:
        json_input = content
    
    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    input_dictionary_list = json_input.get('enrichedDictList',None)
    if isinstance(input_dictionary_list,list)==False:
        return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 


    #json_object = get_json(force=True)
    #input_dictionary_list = json_object['content']
    
    try:  
        for inner_dict in input_dictionary_list:
            json_enriched = generate_json_schema(inner_dict)
            json_schema.append(json_enriched)
    except:  
        return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 

   
    content = json_schema
    status = 600
    error = server_errors[str(status)]
    output = json.dumps({'content' : content,  'error' : error })   
    
    if status <700:
        REST_STATUS = 200
    else:
        REST_STATUS = 500
   
    return output, REST_STATUS, {'Content-Type': 'application/json; charset=utf-8'}   
   
    
################################################
######## enrichment flow apps   ################
################################################
#1
# lemmatizer app
@app.route('/prs-improving-requirements-quality-features/parsing/lemmatizer/<string:extr_type>', methods=['POST'])
def parsing_lemmatizer(extr_type=None):


    """
        Text lemmatization.
        Get a list of text, return a list of lemmatized text.
        ---
        parameters:
          - name: extr_type
            in: path
            description: Language en for english or it for italian.
            required: true
            schema:
              type: string            
          - in: body
            name: body
            schema:
              type: object
              properties:
                documents:
                  type: array
                  items:
                    type: string
                selectedPOS: 
                  type: array
                  items:
                    type: string
                removeStopwords:
                  type: array
                  items:
                    type: string
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: object
                  properties: 
                    lemmatizedDocuments:
                      type: array
                      items:
                        type: array
                        items:
                          type: string
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
    
    language = None
    if (extr_type is None):
        language = "en"
    elif (extr_type == "it"):
        language = "it"
    elif (extr_type == "en"):
        language = "en"

    lem.lang=language
   
    json_input = request.get_json(force=True)

    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    # check validity of input document
    documents = json_input.get('documents',[])
    if isinstance(documents,list) == False or len(documents)==0:
         return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
          
    # check validity of pos list
    pos_list = json_input.get('selectedPOS',None)
    if isinstance(pos_list,list):
        lem.pos_list = pos_list
 
    # check validity of stopwords list
    stopwords_list = json_input.get('removeStopwords',None)
    if isinstance(stopwords_list,list):
        lem.stopwords_list = stopwords_list
    
    
    # apply lemmatizer
    try:
        lemmatized_docs = lem.lemmatize(sentences_list=documents)
    except:
        return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 

    return json.dumps({'content': {'lemmatizedDocuments':lemmatized_docs}, 'error': server_errors["600"] }), 200, {'Content-Type': 'application/json; charset=utf-8'}



#2
# supervised keyords extraction app
@app.route('/prs-improving-requirements-quality-features/parsing/keywords/supervised/<string:extr_type>', methods=['POST'])
def parsing_db_entities_extraction(extr_type = None):

    """
        DbPedia entities extraction.
        Get a text, return dbpedia entities.
        ---
        parameters:
          - name: extr_type
            in: path
            description: Language en for english or it for italian.
            required: true
            schema:
              type: string 
          - in: body
            name: body
            schema:
              type: object
              properties:
                document:
                  type: string
                  description: Parsed Text
                confidence:
                  type: number
                customEntities:
                  type: array
                  items:
                    type: string 
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: object
                  properties: 
                    dbpediaUri:
                      type: array
                      items:
                        type: string
                    dbpediaEntities:
                      type: array
                      items:
                        type: string 
                    patternMatching:
                      type: array
                      items:
                        type: string
                    normalizedDocument:
                      type: string
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
   
    
    language = None
    if (extr_type is None):
        language = "en"
    elif (extr_type == "it"):
        language = "it"
    elif (extr_type == "en"):
        language = "en"
        
    # check validity of input json
    json_input = request.get_json(force=True)
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    document = json_input.get('document',None)
    # check validity of input document
    if isinstance(document,basestring) == False or len(document)==0 :
        return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}
      
  
    # extract confidence and check its validity
    confidence = json_input.get('confidence',config_parameters['ske']['dbp_confidence'])
    if isinstance(confidence,(float,int))==False or confidence >= 1 or confidence <= 0:
        return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}
  
    custom_entities = json_input.get('customEntities',[])
    if isinstance(custom_entities,list) == False:
          return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}

    if (language == "en"):
        dbpediaspotlight_url= config_parameters['ske']['dbpediaspotlight_url_en']
    else:
        dbpediaspotlight_url= config_parameters['ske']['dbpediaspotlight_url_it']
    
    
    try:
        uri, entities, patterns, text = get_output_dbpedia(document=document, 
                                                           tc=tc, 
                                                           confidence=confidence, 
                                                           custom_entities= custom_entities, 
                                                           dbpediaspotlight_url = dbpediaspotlight_url, 
                                                           useProxy=config_parameters['ske']['use_proxy'])
    except:
         return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}


    # define content
    content = {
            'dbpediaUri' : uri,
            'dbpediaEntities'  : entities,
            'patternMatching'  : patterns,
            'normalizedDocument' : text
            }
    return json.dumps({'content': content, 'error' : server_errors['600']}) , 200, {'Content-Type': 'application/json; charset=utf-8'} 


#3
#dbpedia entities type app
@app.route('/prs-improving-requirements-quality-features/parsing/types', methods=['POST'])
def parsing_db_entity_types():

    """
        Get entities types.
        Get a list of entities, return a dict
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                listOfEntities:
                  type: array
                  items:
                    type: string                  
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: object
                  properties: 
                    typeDict:
                      type: object
                      properties:
                        entity i:
                          type: array
                          items:
                            type: string         
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
   
    json_input = request.get_json(force=True)
   
    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    # check validity of input document
    list_of_entities = json_input.get('listOfEntities',None)
    if isinstance(list_of_entities,list) == False:
         return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
     
    # apply 
    try:
       dict_type = preproc_enrich.dbpedia_entity_types(list_of_entities)
    except:
       return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
           

    return json.dumps({'content': {'typeDict':dict_type}, 'error': server_errors["600"] }), 200, {'Content-Type': 'application/json; charset=utf-8'}



#5
# extract features app
@app.route('/prs-improving-requirements-quality-features/parsing/features', methods=['POST'])
def parsing_extract_features():

    """
        Extract features.
        Get a text, return a list of dict with structured paragraph.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                document:
                  type: string               
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: object
                  properties: 
                    featuresDict:
                      type: object                                             
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """

   

   
    json_input = request.get_json(force=True)
   
    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    # check validity of input document
    document = json_input.get('document',None)
    if isinstance(document,basestring) == False:
         return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
     
         
    # apply 
    try:
        for i in range(len(wordlist_list)):
            features_dict  = extract_features([document], wordlist_list[i])[0]
    except: 
        return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'}
     
    return json.dumps({'content': {'featuresDict':features_dict}, 'error': server_errors["600"] }), 200, {'Content-Type': 'application/json; charset=utf-8'}


#6
#formal get structure app
@app.route('/prs-improving-requirements-quality-features/parsing/structure', methods=['POST'])
def parsing_paragraph_structure():

    """
        Document Structure
        Get a text, return a dict with structure.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                document:
                  type: string
                  description: Parsed Text 
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content:
                  type: object
                  properties:
                    paragraphDict:
                      type: array
                      items:
                        type: object  
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                                    
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object                                           
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
    json_input = request.get_json(force=True)
   
    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    # check validity of input document
    document = json_input.get('document',None)
    if isinstance(document,basestring) == False:
         return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
     
    # apply 
    try:
        paragraph_dict= verb_arguments_parser.calculate_paragraph_structure(document)
    except:   
        return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 

    return json.dumps({'content': {'paragraphDict':paragraph_dict}, 'error': server_errors["600"] }), 200, {'Content-Type': 'application/json; charset=utf-8'}



#7
#formal metrics app
@app.route('/prs-improving-requirements-quality-features/parsing/metrics', methods=['POST'])
def parsing_formal_metrics():

    """
        Calculate metrics of parsed text
        Get a text, return a dict with ease and kincaid metric.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                document:
                  type: string
                  description: Parsed Text 
            required: true
        responses:
          200:
            description: Application run normally
            schema:
              type: object
              properties:
                content: 
                  type: object
                  properties: 
                    dictMetrics:
                      type: object
                      properties:
                        ease:
                          type: number
                        kincaid:
                          type: number 
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string                                       
          500:
            description: Internal Server Error
            schema:
              type: object
              properties:
                content: 
                  type: object
                error:
                  type: object
                  properties: 
                    status: 
                      type: number
                    code: 
                      type: string
                    description:
                      type: string  
           

    """
   


   
    json_input = request.get_json(force=True)
   
    # check validity of input json
    if isinstance(json_input, dict) == False:  
        return json.dumps({'content': {}, 'error' : server_errors['707'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
    
    # check validity of input document
    document = json_input.get('document',None)
    if isinstance(document,basestring) == False or len(document)==0:
         return json.dumps({'content': {}, 'error' : server_errors['702'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
     
    # apply formal metrics
    try: 
        dict_metrics = formal_metrics(document)
    except:
        return json.dumps({'content': {}, 'error' : server_errors['705'] }), 500, {'Content-Type': 'application/json; charset=utf-8'} 
   

    return json.dumps({'content': {'dictMetrics':dict_metrics}, 'error': server_errors["600"] }), 200, {'Content-Type': 'application/json; charset=utf-8'}



    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=False, use_reloader=True, threaded=True)
