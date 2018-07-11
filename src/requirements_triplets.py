# -*- coding: utf-8 -*-
from codecs import open
import spacy
from spacy.symbols import nsubj, VERB, dobj, ADP, DET, NOUN
import os
from collections import defaultdict
import sys



class EnglishPredicateArguments(object):
#aggiungi self come primo argomento

    def __init__(self, model_name): 
        self.nlp = spacy.load(model_name)
    
    
    def count_articles(self, list_of_texts):
        '''Gets a list of unicode documents in input and returns a dictionary with a number associated to each document; initializes each document with the spacy nlp() function.'''
        dictionary_of_texts = {}
        for i, doc in enumerate(self.nlp.pipe(list_of_texts, n_threads=4)):
            dictionary_of_texts[i] = doc
        return dictionary_of_texts
        

        
    #funzione crea tokenizzazione e tinei traccia del doc   
    def return_texts_with_index(self, dictionary_of_texts):
        for n_doc, doc in dictionary_of_texts.iteritems():
            yield n_doc, doc


    #tokenizzo e ricavo numero di riga           
    def tokenize_sentences(self, dictionary_of_texts):
        sentence_container = defaultdict(list)
        for n_doc, doc in self.return_texts_with_index(dictionary_of_texts):
            for n_sent, sent in enumerate(doc.sents):
                sentence_container[n_doc].append({n_sent : sent})
        return sentence_container


    @staticmethod
    def create_dictionary(token,  new_dict, dependence = None, subj=None, extended_subj=None):

        new_dict['hash_number'] = token.orth
        prefix = ''
        for child in token.children:
            if "auxpass" == child.dep_:
                prefix = child.text + ' '
        new_dict['verbs'] = prefix + token.text
        new_dict['lemmatized_verb'] = token.lemma_
        for child in token.children:

            if child.dep_ == 'nsubj':
                new_dict['subjects'].append(child.text)
                new_dict['subjects_extended'].append(" ".join([element.text for element in child.subtree]))
            if child.dep_ == 'nsubjpass':
                new_dict['subjects'].append(child.text)
                new_dict['subjects_extended'].append(" ".join([element.text for element in child.subtree]))
            if child.dep_ == 'dobj':
                new_dict['objects'] = child.text
                new_dict['objects_extended'].append( " ".join([element.text for element in child.subtree]) )
            if child.dep_ == 'agent':
                new_dict['objects'].append(' '.join([subchild.text for subchild in child.children if subchild.dep_ == 'pobj']))
                new_dict['objects_extended'].append(' '.join([child.text, ' '.join([subchild.text for subchild in child.children])])) # controlla la sintassi di append()
            if child.pos_ == 'ADJ':
                new_dict['adjectives'].append(child.text)
            if child.pos_ == 'VERB' and child.dep_ in ['advcl', 'ccomp', 'csubj', 'csubjpass', 'conj', 'rcmod', 'xcomp',
                                                       'relcl', 'acl', 'conj']:
                new_dict['subordinates'].append(child)
            if (dependence is not None):
                new_dict["dependence"] = dependence
            if subj is not None:
                new_dict['subjects'] = subj
                if len(new_dict['subjects']) == 0:
                    new_dict['subjects'].extend(subj)
            if extended_subj is not None:
                new_dict['subjects_extended'] = extended_subj
                if len(new_dict['subjects']) == 0:
                    new_dict['subjects_extended'].extend(extended_subj)
        return new_dict, new_dict['subjects'], new_dict['subjects_extended']



    def generate_empty_dict(self):

         new_dict_sub = {'hash_number': '', 'verbs': '', 'lemmatized_verb': '', 'subordinates': [],
                    'subjects': [],
                    'objects': [], 'subjects_extended': [], 'objects_extended': [], 'adjectives': [],
                    'dependence': []}
         return new_dict_sub



    def extract_impersonal_verbs_and_subordinates(self, token, new_dict, dependence=None, subj=None, extended_subj=None):
        doc_list = []

        if token.pos_ == 'VERB':
            result = self.create_dictionary(token, new_dict, dependence, subj, extended_subj)
            new_dict, subject_main_sentence, extended_subject_main_sentence = result

            new_subj = subject_main_sentence if subj is None else subj
            new_extended_subj = extended_subject_main_sentence if extended_subj is None else extended_subj

            if len(new_dict['subordinates']) == 0:
                doc_list.append(new_dict)
                #embed()
                return doc_list
            else:
                doc_list.append(new_dict)
                for c_token in new_dict['subordinates']:
                    #print token.text + " -> " + c_token.text
                    new_dict_sub = self.generate_empty_dict()
                    c_doc = self.extract_impersonal_verbs_and_subordinates(c_token, new_dict=new_dict_sub,
                                                                   dependence=new_dict["hash_number"], subj=new_subj,
                                                                   extended_subj=new_extended_subj)


                    doc_list.extend(c_doc)
                return doc_list

        return doc_list




    def extract_main_verbs(self, sentence_container):
        dict_of_verbs = defaultdict(list)

        for c_doc in sentence_container.values():
            for c_sentence_dict in c_doc:
                for key, value in c_sentence_dict.iteritems():
                    for c_token in value:
                        if c_token.dep_ == "ROOT":
                            dict_of_verbs[key].append(c_token)
        return dict_of_verbs







    def english_parse_sentence_and_get_verb_and_arguments(self, list_of_texts):
        new_triplet_structure = []
        dict_of_docs = self.count_articles(list_of_texts)
        ready_sentences = self.tokenize_sentences(dict_of_docs)

        main_verbs = self.extract_main_verbs(ready_sentences)

        svo_data_structure = defaultdict(list)
        list_of_verbs = [ val[0] for val in main_verbs.values() ]
        for key, verb in enumerate(list_of_verbs):

            #print("MAIN VERB: " + verb.text)
            triplet_structure = self.extract_impersonal_verbs_and_subordinates(verb, self.generate_empty_dict(),
                                                                               dependence=None, subj=None,extended_subj=None)



            for c_element in triplet_structure:
                c_element.pop("subordinates", None)
                new_triplet_structure.append(c_element)

            svo_data_structure[key].extend(new_triplet_structure)
        return new_triplet_structure

        #return svo_data_structure



#questa è la funzione che deve chiamare Nelli,
#passando verb_arguments_parser
#  nel before_first_request
#  verb_arguments_parser = EnglishPredicateArguments('en_core_web_sm')
    def calculate_paragraph_structure(self, text):
        return self.english_parse_sentence_and_get_verb_and_arguments([text])



if __name__ == '__main__':
    #english_input_list = u'All infrastructure conduits which intersect with the railway line or are parallel with it, should be protected in their existing position or relocated in a parallel way and put into cable protection pipes.'
    #english_input_list = [u'All infrastructure conduits which intersect with the railway line or are parallel with it, should be protected in their existing position or relocated in a parallel way and put into cable protection pipes. At the place of passing under the existing railway line, the infrastructure conduits should be conducted by drilling and outside of the railway line they should be placed into unearthed ditches.']
    #english_input_list = u'"Railway line Dugo Selo – Križevci is a constituent part of the branch Vb , Paneuropean corridor passed through the territory of the Republic of Croatia and the railway line M201 State border"'
    #english_input_list = u"""For the purposes of works performance in the area with traffic flow, the continuous 8-hour closings of the railway line (principally from 715 am to 1515 pm 	each working day) shall be set up. Exceptionally, depending on the technology and the demands of the specific works performance, the closings of the railway line lasting 12/24/48/72 hours (principally on weekends from  Friday to Monday) shall be approved. Performance of works  in the area with traffic flow  is necessary only in railway line sections which cannot measure more than 5 kilometres, and it can be executed only in one such section at the time."""
    #english_input_list = [u'All infrastructure conduits which intersect with the railway line or are parallel with it, should be protected in their existing position or relocated in a parallel way and put into cable protection pipes. At the place of passing under the existing railway line, the infrastructure conduits should be conducted by drilling and outside of the railway line they should be placed into unearthed ditches. Infrastructure conduits should be protected under two tracks. \n", "\uf02d\tGas pipelines\n", "Gas pipeline along Rimski put DN 80 diverses along the existing gas pipeline in km 2+328.70 in total length of 39 m and the gas pipeline in Prikraj diverses along the existing gas pipeline in km 6+927.00 in total length of 25.90 m. The gas pipeline along the Andrilove\u010dka Street in km cca 4+552.08 is positioned in a row whose length allows for the construction of the second track. The old gas pipeline along the Ivani\u0107gradska Street is abandoned. New gas pipeline in km cca 6+270 is laid in a protected pipe beneath the existing and designed track.\n']
    #english_input_list = [u'Infrastructure conduits should be protected under two tracks. \n", "\uf02d\tGas pipelines\n", "Gas pipeline along Rimski put DN 80 diverses along the existing gas pipeline in km 2+328.70 in total length of 39 m and the gas pipeline in Prikraj diverses along the existing gas pipeline in km 6+927.00 in total length of 25.90 m. The gas pipeline along the Andrilove\u010dka Street in km cca 4+552.08 is positioned in a row whose length allows for the construction of the second track. ']
    #english_input_list = u'Span structure of the bridge is made from steel plate girders, and bridge abutments are of reinforced concrete with parallel wing walls.'
    #english_input_list = u'The railway station is lit and other electric power plants are fed from the existing outside box +G.EROKP-H\u017d set in the southwest front of the transport office'
    #english_input_list =  u"All infrastructure conduits  which intersect with the rail or are parallel with it should be protected in existing position or parallely relocated and put into protective pipes. At the passing place under the existing rail infrastructure conduits should be passed by drilling and outside of the rail be put into dug-out ditch."
    #u"On the east side of the railway station along the railway-road crossing gas pipeline d160 should be placed by putting into a row, steel protective pipe DN 250 25 m in length at the passing under the rail. At the ends of the row valve shafts should be built in.\n", "Between the gas pipeline and the railway-road crossing leads a water pipeline. It is necessary to relocate it and place it into a steel protective pipe \u00d8300 mm, 27 m long and wih accompanying valve shafts. Through the piping a water pipe 150 mm in diameter is assembled. The passing under the railway station should be drilled.\n", "At the passing under the rail electronic communications should be protected by placing 2 PEHD pipes \u00d850 mm and by slipping through a new cable through one pie. At the ends of both sides of the rail cable shafts should be built in and the new cable connected to the existing. There are 2 passings at the railway station.\n", "Superstructure on an open railway line and at the railway station Vrbovec is planned to be constructed of new rails of type 60 E1 on new prestressed reinforced-concrete and elastic track fixing tools. The rails are welded into the 2nd lane.\n", "At the railway station new switches OL-60E1-500-1:12 and prestressed reinforced-concrete switch beds with elastic track fixing tools will be immediately fixed (with supporting plates). At the railway station 12 switches should be dismantled and 22 new switches OL-60E1-500-1:12 on concrete beds should be built in.\n", "Ballast bed is of least thickness under the track bed where the track is lower than 30 cm in the rail frame. Crushed stone is placed onto the protective layer. Along the railway station chosen thickness of the protective layer is 50cm. Under the protective layer geotextile and geonetwork are placed onto adapted foundation. In the places of extension of the railway station the protective layer is placed onto reinforced embankment. Before the construction of embankment for extension of the railway station 30 cm thick humus should be removed, formation level of the foundation should be adapted according to dimensions from the longitudinal and transverse profiles and cover the depressions with dug out material according to the conditions from the geotechnical project and put geotextile and olypropylene geonetwork under the designed embankment.\n"
    english_input_list = u"For the purposes of works performance in the area with traffic flow, the continuous 8-hour closings of the railway line (principally from 715 am to 1515 pm 	each working day) shall be set up. Exceptionally, depending on the technology and the demands of the specific works performance, the closings of the railway line lasting 12/24/48/72 hours (principally on weekends from  Friday to Monday) shall be approved. Performance of works  in the area with traffic flow  is necessary only in railway line sections which cannot measure more than 5 kilometres, and it can be executed only in one such section at the time."
    verb_arguments_parser = EnglishPredicateArguments('en_core_web_sm')
    #prova = verb_arguments_parser.count_articles(new_input)
    #prova2 = verb_arguments_parser.tokenize_sentences(prova)
    #svo_dictionary = verb_arguments_parser. english_parse_sentence_and_get_verb_and_arguments(new_input)
    prova3 = verb_arguments_parser.calculate_paragraph_structure(english_input_list)
    print prova3
    import json
    prova4 = json.dumps(prova3)
    print prova4