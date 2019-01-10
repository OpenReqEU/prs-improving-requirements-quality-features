#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 14:57:24 2018

@author: francesco pareo
@location: bologna
"""


import re
import pandas as pd
import pattern.en as patternEN
import requests
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import SnowballStemmer
from nltk.corpus import wordnet
import pickle
  
    
    
class OpenNLP_Tagger(object):
    """
    This function returns the POS (Part-Of-Speech) of a token. 
    This function wraps a java openNLP rest service on mn03. 
    It works only for Italian language.
    For more information on POS see: see http://medialab.di.unipi.it/wiki/Tanl_POS_Tagset
        
    Args:
        'proxy_setup' (string): a sting like this: http://user:passwd@proxy.eng.it:port
            
        'chunk_size' (int): chunk size for java opennlp rest service
    """
    def __init__(self, proxy_setup = None, chunk_size=500, service_address = "http://193.109.207.65:15026/tag"):
        self.proxy_setup = proxy_setup
        self.chunk_size = chunk_size
        self.service_address = service_address
    
    def tag(self, sentences_list):
        """
        This function accepts a list of sentences and returns a list of tagged sentences. 
        A tagged sentence is a list of tuple = (token, POS), 
        POS can be: [ X, V, S, R, P, I, F, E, D, C, B, A ] for more infomations see http://medialab.di.unipi.it/wiki/Tanl_POS_Tagset

        Args:
            'sentences_list' (list): list of texts 
                
            'chunk_size' (int): chunk size for java opennlp rest service
        Returns:
            'tagged_sentences' (list): list of list of tuple (token, POS). 
                    tagged_sentences list has the same length of sentences_list
        """
        # separate punctuation from text
        myRegex = re.compile(r'([\':;?!.,])')
        sentences_list = [myRegex.sub(string = x, repl = r' \1 ') for x in sentences_list]; del x
        
        openNLP_call = []
        # OpenNLP rest call runs on limit size dataset
        # we divide dataset in chunks of chunk_size
        if len(sentences_list)<=self.chunk_size:
            openNLP_call = requests.post(self.service_address, 
                                         json={'sentences':sentences_list}, 
                                         headers={'Content-Type':"application/json"}, 
                                         proxies={'http':self.proxy_setup}).json()[0]
        else:
            sentences_list = [sentences_list[x:x+self.chunk_size] for x in xrange(0, len(sentences_list), self.chunk_size)]
            for n,sent_chunk in enumerate(sentences_list): 
                print('Process '+str(n+1)+' chunk of '+str(len(sentences_list)))
                openNLP_chunk = requests.post(self.service_address, 
                                               json={'sentences':sent_chunk}, 
                                               headers={'Content-Type':"application/json"}, 
                                               proxies={'http':self.proxy_setup}).json()[0]

                openNLP_call = openNLP_call+openNLP_chunk

        # from json to list of tuple
        tagged_sentences = [zip(elem['tokens'],[tag[0].upper() for tag in elem['tags']]) for elem in openNLP_call]
        
           
        return tagged_sentences
    
    
    
    
class Lemmatizer(object): 
    """
    This function returns the root definition of a token, i.e. the lemma. 
    The lemmatizer works only for english and italian language. 
    Italian lemmatizer uses Java OpenNLP for POS tagging (see OpenNLP_Tagger above) and
    Morph-it for lemmatizing.
    English version uses pattern python package for POS tagging and WordNet for lemmatizing. 
    
    A stemmer function is also included.
    
    Args:
        'lang' (string): can be 'it' or 'en'
            
        'fast' (bool): if True the function lemmatize without pos tagging 
        
        'chunk_size' (int): chunk size for java opennlp rest service
                   
        'proxy_setup' (string): a sting like this: http://user:passwd@proxy.eng.it:port
            
        'rm_stopwords' (bool or list): removes stopwords in text
            'True' : remove stopwords using spacy
             list : remove stopwords contained in list
             
        'stopwords_list' (list): list of words that wil be removed
        
        'pos_list' (list): list of POS (Part-Of-Speech) that wil be selected 
                            * italian POS : [ X, V, S, R, P, I, F, E, D, C, B, A ] see http://medialab.di.unipi.it/wiki/Tanl_POS_Tagset
                            * english POS : [ J, V, N R ] that are adj, verb, noun and adv 
    """
    
    def __init__(self,lang='it', fast=True, proxy_setup=None, chunk_size=300, service_address = "http://193.109.207.65:15026/tag", stopwords_list=None, pos_list=None):
        self.lang = lang
        self.fast = fast
        self.proxy_setup = proxy_setup
        self.chunk_size = chunk_size
        self.service_address = service_address
        self.morphit_dict = dict()
        self.pos_list = pos_list
        self.stopwords_list = stopwords_list
        self.tagger = OpenNLP_Tagger(proxy_setup=self.proxy_setup, chunk_size=self.chunk_size, service_address = self.service_address)

    @staticmethod
    def __read_POS_decoder__(decoder_POS_file):
        df = pd.read_csv(filepath_or_buffer=decoder_POS_file)
        df.colums = ['from','to']
        return df.set_index('from')['to'].to_dict()


    def process_morphit(self,morphit_file,decoder_POS_file):
        """
        This function takes morphit file and converts Morph-it POS codes
        as openNLP POS codes using decoder_POS_file.
        """
        # read POS decoder file
        decoder_dict = Lemmatizer.__read_POS_decoder__(decoder_POS_file)
        ### 1 - generate morphit dataframe
        morphit_df = pd.read_table(filepath_or_buffer=morphit_file,
                                   delimiter='\t',header=-1,encoding='UTF-8',index_col=False)
        morphit_df.columns=['token','lemma','POS']
        morphit_df.token = morphit_df.token.str.lower()
        morphit_df.lemma = morphit_df.lemma.str.lower()
        # drop null values
        morphit_df = morphit_df.dropna(axis=0)
        # cleaning lemma and token 
        morphit_df['token'] = [re.sub(pattern=r"['-]", repl="", string=word) for word in morphit_df['token']]
        morphit_df['lemma'] = [re.sub(pattern=r"['-]", repl="", string=word) for word in morphit_df['lemma']]
        # cleaning and decode POS
        morphit_df['POS'] = morphit_df['POS'].apply(lambda x: re.search(pattern='^.*?(?=:|-|$)',string=x).group(0))
        morphit_df['POS'] = morphit_df['POS'].apply(lambda x: decoder_dict[x])
        # drop duplicated values (token-POS)
        morphit_df_token_POS = morphit_df.drop_duplicates(subset=['token','POS'], keep='first', inplace=False)
        # drop duplicated values (token)
        morphit_df_token = morphit_df.drop_duplicates(subset=['token'], keep='first', inplace=False)
        morphit_df_token['POS'] = u"ALTRO"
        # merge the two dataframes and create a dict
        morphit_dict = morphit_df_token_POS.append(morphit_df_token)
        morphit_dict = morphit_dict.drop_duplicates(subset=['token','POS'], keep='first', inplace=False)
        morphit_dict['POS'] = [unicode(x) for x in morphit_dict['POS']]
        morphit_dict = morphit_dict.set_index(['token','POS'])["lemma"]
        morphit_dict = morphit_dict.to_dict()
        self.morphit_dict = morphit_dict

        
    def save_morphit_dict(self, dict_filename):
        """
        This function saves decoded morphit dictonary in pickle format. 
        """
        pickle.dump( self.morphit_dict, open( dict_filename, "wb" ) )

        
    def load_morphit_dict(self, dict_filename, decoder_POS_file):
        """
        This function loads decoded morphit dictonary in pickle format. 
        """
        self.process_morphit( dict_filename, decoder_POS_file )
        #self.morphit_dict = pickle.load( open( dict_filename, 'rb' ) )

        
    @staticmethod    
    def __morphit_POS_lemmatizer__( self, token_list ):
        lemmatized_sent = list()
        for item in token_list:
            out = self.morphit_dict.get( item )
            if out == None:
                out = self.morphit_dict.get( ( item[0],unicode( 'ALTRO' ) ) )
                if out == None: 
                    out = item[0]
            lemmatized_sent.append( out )
        return lemmatized_sent


    @staticmethod
    def __remove_stopwords__( self, lemma_list ):
        new_list = []
        for i in lemma_list:
            if i not in self.stopwords_list:
                new_list.append(i)
        return new_list
    
    
    @staticmethod
    def __select_pos__( self, token_list ):
        new_list = []
        for i in token_list:
            if i[1] in self.pos_list:
                new_list.append(i)
        return new_list
    
    
    @staticmethod
    def __morphit_fast_lemmatizer__( self, token_list ):
        lemmatized_sent = list()
        for item in token_list:
            out = self.morphit_dict.get((item,unicode('ALTRO')))
            if out == None: 
                out = item
            lemmatized_sent.append(out)
        return lemmatized_sent


    @staticmethod
    def __WNLPOSDecoder__(treebank_tag):
        if treebank_tag.startswith( 'J' ):
            return wordnet.ADJ
        elif treebank_tag.startswith( 'V' ):
            return wordnet.VERB
        elif treebank_tag.startswith( 'N' ):
            return wordnet.NOUN
        elif treebank_tag.startswith( 'R' ):
            return wordnet.ADV
        else:
            return wordnet.NOUN

        
    @staticmethod    
    def __WNL_POS_lemmatizer__(self, text):
        tagged_text = patternEN.tag(text)
        WNL = WordNetLemmatizer()
        if self.pos_list is not None and isinstance(self.pos_list,list):
            tagged_text = [WNL.lemmatize(elem[0],Lemmatizer.__WNLPOSDecoder__(elem[1])) for elem in tagged_text if elem[1][0] in self.pos_list]
        else:
            tagged_text = [WNL.lemmatize(elem[0],Lemmatizer.__WNLPOSDecoder__(elem[1])) for elem in tagged_text]

        return tagged_text


    def lemmatize( self, sentences_list ):   
        """
        This function accepts a list of sentences and returns a list of lemmatized sentences. 
        A lemmatized sentence is a list of lemmas, i.e a list of token root.

        Args:
            'sentences_list' (list): list of texts 
                
        Returns:
            'lemmatized_sen' (list): list of list of lemmas
        """
        if self.lang=='it':
            if self.morphit_dict == dict():
                raise ValueError, 'Needs a Morphit dictionary, use "load_morphit_dict" function'
            if self.fast:
                tokenized_sen = [word_tokenize(language='italian',text=sen) for sen in sentences_list]
                lemmatized_sen = [Lemmatizer.__morphit_fast_lemmatizer__(self,token_list=sen) for sen in tokenized_sen]
                
            else:
                tagged_sen = OpenNLP_Tagger(proxy_setup=self.proxy_setup, chunk_size=self.chunk_size).tag(sentences_list)
                if self.pos_list is not None and isinstance(self.pos_list,list):
                    tagged_sen = [Lemmatizer.__select_pos__(self,token_list=sen) for sen in tagged_sen]
                lemmatized_sen = [Lemmatizer.__morphit_POS_lemmatizer__(self,token_list=sen) for sen in tagged_sen]

        elif self.lang=='en':
            lemmatized_sen = [Lemmatizer.__WNL_POS_lemmatizer__(self,sen) for sen in sentences_list]
            
        if self.stopwords_list is not None and isinstance(self.stopwords_list,list):
            lemmatized_sen = [Lemmatizer.__remove_stopwords__(self,lemma_list=sen) for sen in lemmatized_sen]    
        
        return lemmatized_sen 
    
    
    def stemming( self, sentences_list ):
        """
        This function accepts a list of sentences and returns a list of stemmed sentences. 
        This function uses nltk SnowballStemmer.
        Args:
            'sentences_list' (list): list of texts 

        Returns:
            'stemmed_sen' (list): list of list of stemmed token
        """
        if self.lang=='en':
            stemmer_lang = 'english'
        elif self.lang=='it':
            stemmer_lang = 'italian' 
        stemmer = SnowballStemmer( language=stemmer_lang, ignore_stopwords=False )
        stemmed_sen = list()
        for sen in sentences_list:
            tokenized_sen = word_tokenize( language=stemmer_lang, text=sen )
            if self.stopwords_list is not None and isinstance(self.stopwords_list,list):
                stemmed_sen.append( [ stemmer.stem( word.decode('utf-8') ) for word in tokenized_sen if word not in self.stopwords_list ] )
            else:
                stemmed_sen.append( [ stemmer.stem( word.decode('utf-8') ) for word in tokenized_sen ] )
        return stemmed_sen    
