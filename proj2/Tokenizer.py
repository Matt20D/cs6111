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
	
	def __init__(self, url, current_tuples, relation, conf):
		self.webpage       = url
		self.curr_tuples   = current_tuples # Hash Table, value is the confidence
		self.relation_type = relation
		self.threshold     = conf

	def execute_get_request(self) -> None:

		# send get request for the webpage
		try:
			print("\tGetting the webpage using GET request") 
			request = requests.get(self.webpage, timeout=5) # need to timeout and not hang
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
		sentence_num = 1


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
				print("\t\t\tNo valid candidate pairs, no need for Bert")
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
				print("\t\t\t=== Extracted Relation ===")
				#print("[{},{}]".format(ex["subj"], ex["obj"]))
				print("\t\t\tInput Tokens: {}".format(ex['tokens']))
				print("\t\t\tSubject: {}".format(ex["subj"][0]))
				print("\t\t\tObject: {}".format(ex["obj"][0]))
				print("\t\t\tRelation: {}".format(pred[0]))
				print("\t\t\tConfidence: {}".format(pred[1]))

				# lets keep the extracted tuple!
				if pred[1] >= self.threshold:

					print("\t\t\tAdding to set of extracted relations")
					
					new_tuple = (ex["subj"][0], ex["obj"][0])
					new_conf  = pred[1]

					# if not in set, just add it	
					if new_tuple not in self.curr_tuples.keys():
					
						self.curr_tuples[new_tuple] = new_conf

					# if in set, keep the higher confidence version
					else:
						#print("already in set")
						#print("old conf: {}".format(self.curr_tuples[new_tuple]))
						#print("new conf: {}".format(new_conf))
						if self.curr_tuples[new_tuple] < new_conf:
							self.curr_tuples[new_tuple] = new_conf
						#print("after check conf: {}".format(self.curr_tuples[new_tuple]))

				# ignore, move on
				else:
					print("\t\t\tConfidence is lower than threshold confidence. Ignoring this.")

				print("\t\t\t==========================\n")
         	
                         
