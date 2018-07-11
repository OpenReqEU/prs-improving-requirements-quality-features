# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 18:06:34 2018

@author: mgabusi
"""
import re
import json
import os



def is_title(c_line, threshold_uppercase= 0.7):
	original_c_line = c_line

	c_line = re.sub("\W", "", c_line)
	total_len = len(c_line)
	total_upper = 0.
	for letter in c_line:
		if (letter.isupper() | letter.isdigit()) == True:
			total_upper +=1.
	try:
		is_mostly_uppercase = total_upper/total_len > threshold_uppercase
	except:
		is_mostly_uppercase = False
	start_paragraph     = re.match(r'^\d\.[\d\.]+', original_c_line) is not None
	#numbered_title     = re.match(r'^\d+\t', original_c_line) is not None
	return is_mostly_uppercase | start_paragraph 
			
def is_indented(c_line):
	is_indented = False
	if ( (re.match(r'\s', c_line) is not None) | (re.match(r'\d+\.[\d+\.]+', c_line) is not None)) :
		is_indented = True
	return is_indented

def depends_on(active_title, previous_title):
	
	if (active_title.find("\t") < 0):
		return False
		
	previous_title_num = previous_title.split("\t")[0]
	active_title_num = active_title.split("\t")[0]
	
	if (active_title_num.find(previous_title_num) >=0):
		return True
	elif (is_bullet(active_title)):
		return True
	else:
		return False

def is_bullet(c_line):
	is_bullet = False
	
	#here must be listed all the possible regex that may appear as bullet
	if ((re.match(r'^\uf0b7[\t\s+]', c_line) is not None) | (re.match(r'^\u2022[\t\s+]', c_line) is not None) | (re.match(r'^o[\t\s+]', c_line) is not None) | (re.match(r'-[\t\s+]', c_line) is not None) | 
	 (re.match(r'^[a-zA-Z]+\)', c_line) is not None) | (re.match(r'^[a-zA-Z]+\.', c_line) is not None) | (re.match(r'^\([a-zA-Z]+\)', c_line) is not None) |
		 (re.match(r'\u00b7[\t\s+]', c_line) is not None) | (re.match(r'\u2022[\t\s+]', c_line) is not None) ) :
		is_bullet = True
		
	return is_bullet

def parse(f):
#def parse(f_name):
        #path = os.getcwd()+'/../output/'
        #f = open(f_name,'rb')
	state_machine = { "CURRENT_STATE" : "", "PREVIOUS_STATE":"", "PREVIOUS_TITLE":"" } 
	document_struct = []
	current_paragraph = {}
	
	max_n_lines = 1e6
	
	list_of_paragraph = []
	list_of_pid = []
	line_counter = 0
	line_to_skip = 2

	c_title = ""
	cnt_pid = 0
	for line in f:
		if line_counter >= max_n_lines:
			break
		if line_counter < line_to_skip:
			line_counter += 1
			continue
		
		if 	line == "\n":
			state_machine["PREVIOUS_STATE"] = "ENDLINE_LINE"
			line_counter += 1
			continue
		
		#if the last line was an endline, either a new paragraph or a new title may start
		#if (state_machine["PREVIOUS_STATE"] == "ENDLINE_LINE") | (state_machine["PREVIOUS_STATE"] == "TITLE") :
		if line == "\n":
			line_counter += 1
			continue
		else:
			#by default, add 1
			line_counter += 1
			
			if ( is_title(line) == True ):		

				if ( (depends_on(line,state_machine["PREVIOUS_TITLE"]) == False)):

					#just archive current paragraph and start a new one
					document_struct.append(current_paragraph)
					
					#initialize a new paragraph
					c_title = line
					current_paragraph = {}
					list_of_paragraph = []
					
					#se e un nuovo titolo, il titolo attuale diventa la linea
					current_paragraph["Title"] = c_title					
					current_paragraph["Line"] = "L" +  str(line_counter)
					#set the state for the next iteration
					state_machine["PREVIOUS_STATE"] = "TITLE"
					state_machine["PREVIOUS_TITLE"] = c_title
					
				else:
					#set current line as a new title	
					#just archive current paragraph and start a new one
					document_struct.append(current_paragraph)
					
					#initialize a new paragraph
					
					current_paragraph = {}
					list_of_paragraph = []
					
					#se c'e dipendemnza, il titolo attuale diventa la linea corrente
					c_title = line
					current_paragraph["Title"] = c_title	
					current_paragraph["Line"] = "L" + str(line_counter)
					current_paragraph["Dependence"] = state_machine["PREVIOUS_TITLE"]				
					state_machine["PREVIOUS_TITLE"] = c_title	
					
			elif ( is_bullet(line) ):
					
					state_machine["PREVIOUS_STATE"] = "BULLET"
					document_struct.append(current_paragraph)
					current_paragraph = {}
					list_of_paragraph = []
					current_paragraph["Line"] = "L" + str(line_counter)
					current_paragraph["Title"] = state_machine["PREVIOUS_TITLE"]
					current_paragraph["Bullet"] = line
					
			else:	
				
				state_machine["PREVIOUS_STATE"] = "PARAGRAPH"	
				#current_paragraph["Line"] = "L" + str(line_counter)
				cnt_pid += 1
				pid = "P" + str(cnt_pid)
				if ("Paragraphs" not in current_paragraph.keys()):
					list_of_paragraph.append(line)
					list_of_pid.append(pid)
					current_paragraph["Paragraphs"] = list_of_paragraph
					current_paragraph["PID"] = list_of_pid
					
					list_of_pid = []
					list_of_paragraph = []
					
				else:
					current_paragraph["Paragraphs"].append(line)
					current_paragraph["PID"].append(pid)
					
	json_dict = json.dumps (document_struct)
	#with open(f_name + "_format.txt", "w") as f:
	#	f.write(json_dict)
	return  document_struct
       



