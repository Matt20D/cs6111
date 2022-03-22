"""
file: Tokenizer.py
description: Tokenizer class used for parsing html documents into tokens
which is a big part of the document analysis. We need to be able to 
get a list of all the words in a document so that we can create inverted
lists.
authors: Matthew Duran and Ethan Garry
"""

#
# Library Modules Needed
#

import requests # use to execute a get request
from bs4 import BeautifulSoup as bs # scraper
import re # regex
import spacy
from SpanBERT.spacy_help_functions import * #import spacy help
from SpanBERT.spanbert import SpanBERT 

spanbert = SpanBERT("./SpanBERT/pretrained_spanbert")  

RELATIONS = {
	"Schools_Attended": 
		{"Subject": "PERSON", "Object": "ORGANIZATION"},
	"Work_For": 
		{"Subject": "PERSON", "Object": "ORGANIZATION"},
	"Live_In": 
		{"Subject": "PERSON", "Object": ["LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]},
	"Top_Member_Employees": 
		{"Subject": "ORGANIZATION", "Object": "PERSON"}
}

def is_valid_relation(rel_type: str, pair: dict) -> bool:

	#
	# extract types
	#

	# proj type
	obj_type = pair['obj'][1]
	# subject type
	sub_type = pair['subj'][1]


	#
	# type check for a given relation
	#
	if rel_type == "Schools_Attended" or rel_type == "Work_For" or rel_type == "Top_Member_Employees":
		#print(pair)
		#print(rel_type)
		#print(RELATIONS[rel_type])
		if  obj_type == RELATIONS[rel_type]["Object"] and \
			sub_type == RELATIONS[rel_type]["Subject"]:
			return True
		else:
			return False
	elif rel_type == "Live_In":
		#print(pair)
		#print(rel_type)
		#print(RELATIONS[rel_type])
		if  obj_type in RELATIONS[rel_type]["Object"] and \
			sub_type == RELATIONS[rel_type]["Subject"]:
			return True
		else:
			return False
	# a little bit of defensive programming, we should only be getting tuples
	# of the above 4 rel types
	else:
		return False
class Tokenizer(object):
	
	def __init__(self, url, current_tuples, relation):
		self.webpage       = url
		self.curr_tuples   = current_tuples # Do not add anything, just use
											# for checking and size
		self.relation_type = relation 

	def execute_get_request(self) -> None:

		# send get request for the webpage
		try:
			print("\tGetting the webpage using GET request") 
			request = requests.get(self.webpage)
		except:
			# raise exception, so that we just use the stored title and snippet
			raise requests.exceptions.HTTPError

		# if the request status is not "200" ok then throw an exception
		# the code will then simply used the stored snippet and title
		if request.status_code != 200:
			raise requests.exceptions.HTTPError

		# Extract text
		# source: https://www.geeksforgeeks.org/remove-all-style-scripts-and-html-tags-using-beautifulsoup/
		soup = bs(request.text, "html.parser")
 
		for data in soup(['style', 'script']):
			# Remove tags
			data.decompose()

		soup_text = ' '.join(soup.stripped_strings)        
     
		# get first 20k characters as specified in assignment prompt
		print("\tWebpage length (num characters): {}".format(len(soup_text)))
		if len(soup_text) > 2000:
			print("\tTrimming Webpage Content from {} to 2000 characters".format(len(soup_text)))
        
		soup_text = soup_text if len(soup_text)<=20000 else soup_text[:20000]

		print("\tAnnotating the webpage using spacy...")
		nlp = spacy.load("en_core_web_lg")
		doc = nlp(soup_text)
		print("\tExtracted {} sentences.".format(len(doc.sents)))

		entities_of_interest = ["ORGANIZATION", "PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]


		# 3) run the expensive SpanBERT model, separately only over each 
		#    entity pair that contains both required named entities for the relation of interest
		# 4) IMPORTANT: skip SpanBERT for any entity pairs that are missing one or two entities 
		# of the type required by the relation.
		for sentence in doc.sents:

			# 1) use spaCY to ID sentences in web text along with the 
			#    named entities (if any), that appear
			print("\n\n\tProcessing sentence: {}".format(sentence))
			print("\tTokenized sentence: {}".format([token.text for token in sentence]))
			ents = get_entities(sentence, entities_of_interest)
			print("\tspaCy extracted entities: {}".format(ents))

			# 2) Then, you should construct entity pairs
			candidate_pairs = []
			sentence_entity_pairs = create_entity_pairs(sentence, entities_of_interest)
			
			for ep in sentence_entity_pairs:
				
				# generate the pairs
				pair1 = {"tokens": ep[0], "subj": ep[1], "obj": ep[2]}
				pair2 = {"tokens": ep[0], "subj": ep[2], "obj": ep[1]}

				# filter out only subject-object pairs of the right type for the target relation
				pair1_valid = is_valid_relation(self.relation_type, pair1)
				pair2_valid = is_valid_relation(self.relation_type, pair2)

				# if one of the pairs is true, then the other should be false
				if pair1_valid == True:
					# append valid pairs
					candidate_pairs.append(pair1)  # e1=Subject, e2=Object
					continue
				elif pair2_valid == True:
					# append valid pairs
					candidate_pairs.append(pair2)  # e1=Object, e2=Subject
					continue

			print("\tGenerated Sentence entity pairs: {}, remaining valid pairs: {}".format(\
									len(sentence_entity_pairs), len(candidate_pairs)))
			quit()
        #print('working on new doc')
        #try:
        #    relations = extract_relations(doc, spanbert, entities_of_interest)
        #    if len(relations.keys())>0:
        #        print("Relations: {}".format(dict(relations)))
        #        return relations
        #    return None
        #except:
        #    return None

        
    

          
                         
 
