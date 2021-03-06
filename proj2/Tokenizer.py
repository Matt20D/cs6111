"""
File: Tokenizer.py
Description: This file handles executing a get request and doing
information extraction using web scraping, spanBERT and spacy. For
a given url, we will extract sentences, candidate pairs, and then final
spanBert approved relations.
Authors: Matthew Duran and Ethan Garry
"""

#
# Library Modules Needed
#

import requests # use to execute a get request
from bs4 import BeautifulSoup as bs # scraper
import re # regex
import spacy
from spacy_help_functions import * #import spacy help
from spanbert import SpanBERT 

# load spanbert model from my pwd
spanbert = SpanBERT(pretrained_dir="./pretrained_spanbert")

"""
The following global datastructures allow me to do data validation checks
in the below code.
"""
ENTITIES_OF_INTEREST = ["ORGANIZATION", "PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]
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
SPANBERT_RELATIONS = {
	"Schools_Attended": "per:schools_attended",
	"Work_For": "per:employee_of", 		
	"Live_In": 	"per:cities_of_residence",
	"Top_Member_Employees": "org:top_members/employees"
}

"""
desc: 
Given a sentence, lets look at the extracted ents (via spacy) to see
if we can make at least ONE valid subject object pair. If we can then
return true and lets process the sentence further. Else we can return
false to skip the expensive bert calculations.

params:
rel_type: string relation that is passed in so we can determine
if a sentence has enough valid entities to make pairs
ents: list of extracted ents
"""
def check_sentence_entities(rel_type: str, ents: list) -> bool:
	#print(rel_type)
	#print(ents)
	seen_sub = False
	seen_obj = False
	
	# test all entities to ensure that I cover both categories at a MINIMUM
	for ent in ents:
		extracted_ent = ent[1]

		if seen_sub == False:
			# test if this ent is a subject
			if RELATIONS[rel_type]['Subject'] == extracted_ent:
				seen_sub = True

		if seen_obj == False:
			# test if this ent it an object
			if rel_type == "Live_In": 
				# this rel type has a list of objects
				if extracted_ent in RELATIONS[rel_type]['Object']:
					seen_obj = True
			else: 
				# all other rel types have single objects
				if extracted_ent == RELATIONS[rel_type]['Object']:
					seen_obj = True

	#print("seen_sub: {}".format(seen_sub))
	#print("seen_obj: {}".format(seen_obj))
	# determine if we are missing one or two of the entities required by the 
	# relation
	if seen_sub == True and seen_obj == True:
		return True
	else:
		return False

"""
desc: 
Given a pair, lets ensure that the subject and object will actually
form a valid relation (i.e. what we are looking for).

params:
rel_type: string relation that is passed in so we can determine
if a sentence has enough valid entities to make pairs
pair: map of data to check
"""
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

"""
desc: Tokenizer class that handles get request and data parsing.
"""
class Tokenizer(object):
	
	"""
	desc: constructor
	params:
	url: webpage link
	currenct_tuples: the full list of extracted relations
	relation: the type of relation we are searching for
	conf: threshold to keep a relation
	"""
	def __init__(self, url, current_tuples, relation, conf):
		self.webpage       = url
		self.curr_tuples   = current_tuples # Hash Table, value is the confidence
		self.relation_type = relation
		self.threshold     = conf

	"""
	desc: handle the get request and do the web scraping and 
	information extraction
	"""
	def execute_get_request(self) -> None:

		# send get request for the webpage
		try:
			print("\tGetting the webpage using GET request") 

			# by adding in the headers, we may not get denied by certain webpages
			# also upping the timeout to 20 like the TA mentions
			request = requests.get(self.webpage, headers={'User-Agent': 'Mozilla/5.0'},\
												timeout=20) # need to timeout and not hang
		except:
			# raise exception, which is a catch all for timeouts or other http errors
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
		#print("\tExtracted {} sentences.".format(len(doc.sents)))

		# book keeping
		sentence_num       = 1
		num_tuples_added   = 0

		for sentence in doc.sents:
			

			# 1) use spaCY to ID sentences in web text along with the 
			#    named entities (if any), that appear
			#print("\n\n\tProcessing sentence: {}".format(sentence))
			#print("\tTokenized sentence: {}".format([token.text for token in sentence]))
			ents = get_entities(sentence, ENTITIES_OF_INTEREST)
			#print("\tspaCy extracted entities: {}".format(ents))

			# 2) IMPORTANT: skip SpanBERT for any entity pairs that are missing one or
			#    two entities of the type required by the relation. Dont waste time
			if check_sentence_entities(self.relation_type, ents) == False:
				#print("\t\t\tSkipping sentence {}. Missing one or more "\
				#			"extracted entities for relation".format(sentence_num))
				sentence_num += 1 # even tho we skip, still book mark
				continue
			else:
				# book keep sentence 
				print("\t\tProcessing sentence {}".format(sentence_num))
				sentence_num += 1

			# 3) Then, you should construct entity pairs
			candidate_pairs = []
			sentence_entity_pairs = create_entity_pairs(sentence, ENTITIES_OF_INTEREST)
			
			# 4) Filter out invalid pairs
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

			print("\t\t\tGenerated Sentence entity pairs: {}, remaining "\
				"valid pairs: {}".format(len(sentence_entity_pairs), len(candidate_pairs)))
			
			if len(candidate_pairs) == 0:
				print("\t\t\tNo valid candidate pairs, no need for Bert\n")
				continue
			#else:
			#	print("Candidate entity pairs:")
			#	for p in candidate_pairs:
			#		print("Subject: {}\tObject: {}".format(p["subj"][0:2], p["obj"][0:2]))

			# 5) run the expensive SpanBERT model, separately only over each 
			#    entity pair that contains both required named entities for the relation of interest
			print("\t\t\tApplying SpanBERT for each of the {} candidate pairs. "\
							"This should take some time...\n".format(len(candidate_pairs)))

			# get predictions: list of (relation, confidence) pairs 
			relation_preds = spanbert.predict(candidate_pairs)     

			# Print Extracted Relations
			for ex, pred in list(zip(candidate_pairs, relation_preds)):
				if pred[0] == SPANBERT_RELATIONS[self.relation_type]:				
				#if pred[0] != "no_relation":				
					print("\t\t\t=== Extracted Relation ===")
					print("\t\t\tSubject Entity: {}".format(ex["subj"][1]))
					print("\t\t\tObject Entity: {}".format(ex["obj"][1]))
					print("\t\t\tInput Tokens: {}".format(ex['tokens']))
					print("\t\t\tSubject: {}".format(ex["subj"][0]))
					print("\t\t\tObject: {}".format(ex["obj"][0]))
					print("\t\t\tRelation: {}".format(pred[0]))
					print("\t\t\tConfidence: {}".format(pred[1]))

					# lets keep the extracted tuple, hopefully!
					if pred[1] >= self.threshold:

						
						new_tuple = (ex["subj"][0], ex["obj"][0])
						new_conf  = pred[1]

						# if not in set, just add it	
						if new_tuple not in self.curr_tuples.keys():

							print("\t\t\tAdding to set of extracted relations")
						
							self.curr_tuples[new_tuple] = new_conf
							num_tuples_added += 1

						# if in set, keep the higher confidence version
						else:
							#print("already in set")
							#print("old conf: {}".format(self.curr_tuples[new_tuple]))
							#print("new conf: {}".format(new_conf))
							if self.curr_tuples[new_tuple] < new_conf:
								print("\t\t\tAlready present but higher confidence. Update it.")
								self.curr_tuples[new_tuple] = new_conf
							else:
								print("\t\t\tAlready present but lower confidence. Discard it.")
							#print("after check conf: {}".format(self.curr_tuples[new_tuple]))

					# ignore, move on
					else:
						print("\t\t\tConfidence is lower than threshold confidence. Ignoring this.")

					print("\t\t\t==========================\n")
         	
		print("\tRelations extracted from this website: {} (Overall: {})\n".format(\
										num_tuples_added, len(self.curr_tuples)))
