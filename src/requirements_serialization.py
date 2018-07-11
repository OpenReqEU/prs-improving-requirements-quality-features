# -*- coding: utf-8 -*-
"""
Created on Tue Jun 05 14:55:28 2018

@author: magafurzyanova
"""

import pyorient

from pyorient.ogm.property import PropertyEncoder

# Supposing that the input would be smth like:
# {'text': 'there is smth written here', 'entities': {('subject', 'object'):['verb1', 'verb2']}}


def entities_to_orient(input):
	subject_entities = []
	object_entities = []
	triple = input['entities']
	for k in tripletta.iterkeys():
		subject_entities.append(k[0])
		object_entities.append(k[1])
	all_entities = list(set(subject_entities+object_entities))	
	for ent in all_entities:
		ins_node_str = u"insert into entity (id) values ({})".format(PropertyEncoder.encode_value(ent))
		ins_node = client.command(ins_node_str)
	

def schema_to_orient(input):
	triple = input['entities']
	for k, v in triple.iteritems():
		try:
			from_node_str = u'select from entity where id={}'.format(PropertyEncoder.encode_value(k[0]))
			from_node = client.command(from_node_str)
			from_node_rid = from_node[0]._rid
			
			try:
				to_node_str = u'select from entity where id = {}'.format(PropertyEncoder.encode_value(k[1]))
				to_node = client.command(to_node_str)
				to_node_rid = to_node[0]._rid
				
				for verb in v:
					try:
						ins_edge_str = "create edge hasVerb from {} to {} set  verb = {}".format(from_node_rid, to_node_rid, verb)
						ins_edge = client.command(ins_edge_str)
					except pyorient.PyOrientORecordDuplicatedException:
						pass
						
			except IndexError:
				failed_to_nodes[k[0]] = k[1]
				pass
		
		except IndexError:
			failed_from_nodes[k[0]]=k[1]
			pass
			
			
