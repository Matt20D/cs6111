"""
file: google-query.py
description: Main Driver for Google Query Relevance Feedback
authors: Matthew Duran and Ethan Garry
"""

#
# Library Modules Needed
#

# from ctypes.wintypes import WORD
# import re # regex
# import pprint # printing out Datastructures in a readable format
# import os
from logging import exception, raiseExceptions
from operator import inv
import sys
from tokenize import String # command line arg parsing
import numpy as np # havent decided which one yet
import pandas as pd # havent decided which one yet
import math # for logs
import Tokenizer # class written to execute get request and get the keywords back
import requests
import heapq # for choosing words
import itertools
from collections import defaultdict
from googleapiclient.discovery import build # for querying google using their API


"""
desc: 
use this method to print all query and API parameters to the console
"""
def print_params(api_key, eid, field_to_extract, confidence_threshold, query, iteration, k) -> None:
	
	print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
	print(" Client Key  				= {}".format(api_key))									
	print(" Engine Key  				= {}".format(eid))
	print(" Field to Extract			= {}".format(field_to_extract))
	print(" Confidence Threshold			= {}".format(confidence_threshold))
	print(" Desired Number of Tuples		= {}".format(k))
	print(" Query       				= {}".format(to_string(query)))
	print(" Iteration   				= {}".format(iteration))
	print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
	print()

"""
desc: 
convert the query list of keywords to a string, used for debugging purposes
"""
def to_string(query_l: list) -> str:
	query_s = ""
	for i in range (0, len(query_l)):
		query_s += query_l[i]
		if i != len(query_l) - 1:
			query_s += " "
	return query_s

"""
desc: 
For a particular iteration, lets pass in the 
correct parameters to execute a google query API

params:
q/query: query input list
cx/eid:  search engine id
key: 	 google API key

citation:
https://github.com/googleapis/google-api-python-client/blob/main/samples/customsearch/main.py
"""
def query_google_search(query: list, eid: str, key: str) -> list():
	
	# use google api for querying
	service = build("customsearch", "v1",
		developerKey=key)

	res  = service.cse().list(
			key = key,
			cx = eid,
			q  = to_string(query)
			).execute()

	# get the actual queries from response document, max of 10 returned always
	queries = res['items']

	# lets parse the data thate we need URL, title, desc from the JSON object
	clean_results = []
	for doc in queries:
		# link has the http/https format which is needed for get request
		clean_results.append(doc['link']) # changed from doc['formattedUrl']

	return clean_results


def extract_sentences(url: String) -> list: # return a list of keywords, after potentially adding at max 2 new
	
	#instantiate tokenizer object
	tk 		= Tokenizer.Tokenizer(url)
	sentences = []
	try:
		# use method to execute get request and return clean document words in list
		sentences = tk.execute_get_request()
			
	except requests.exceptions.HTTPError:
		# on failure we skip
		pass
	return sentences

"""
desc:
main method where program control is run out of.
"""
def main() -> None:

	# ensure that there are at exactly 4 command line arguments + the program run name
	# Query is a string with as many words as desired
	if len(sys.argv) != 7: # changed from ... > 5
		sys.exit(" usage: iterative-set-expansion.py <google API Key> <google engine id> <r> <t> <seed query> <k>")

	# idk if we can even error check this... 
	api_key     = str(sys.argv[1])
	engine_id   = str(sys.argv[2])
	
	# indicates relation to extract
	# 1 for Schools_Attended, 2 for Work_For, 3 for Live_In, 4 Top_Member_Employees
	r   = int(sys.argv[3])
	
	if r == 1:
		relation_to_extract = 'Schools_Attended'
	elif r == 2:
		relation_to_extract = 'Work_For'
	elif r==3:
		relation_to_extract = 'Live_In'
	elif r==4:
		relation_to_extract = 'Top_Member_Employees'
	else:
		sys.exit(" usage: r needs to be 1, 2, 3 or 4")

	# indicates extraction confidence threshold
	# real number between 0 and 1
	t   = float(sys.argv[4])
	if t < 0.0 or t > 1.0:
		sys.exit(" usage: t needs to be 0 and 1")

	# create a query list of keywords
	seed_query 		= sys.argv[5].split()

	# k ==> number of tuples we request in the output
	k   = int(sys.argv[6])
	

	# set up counter for iterations
	num_searches = 1

	# current query
	current_query = seed_query

	# set of extracted tuples
	X = set()

	# run this loop until we hit k tuples
	while len(X) < k:		
		
		# print the params to the console
		print_params(api_key, engine_id, r, t, current_query, num_searches, k)
			
		# execute query ---> returns list of urls
		url_list = query_google_search(current_query, engine_id, api_key)
		
		# extract sentences and use spaCy to split text into sentences
		for url in url_list:
			extracted_sentences = extract_sentences(url)		
		
		# feed sentences and named entity pairs as input to SpanBERT 
		# to predict the corresponding relations and extract all instances 
		# of the relation specified by input param r

		print()

		# increment the iteration counter
		num_searches += 1

	# return from main
	#return

"""
main driver for the program
"""
if __name__ == "__main__":
	
	try:

		# print greeting
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("+                      Welcome to Iterative Set Expansion			            +")
		print("+                     Written by Matt Duran and Ethan Garry                      +")
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		
		# run the program
		main()

	# control-c graceful exit
	except KeyboardInterrupt:
		
		print("\n")
	
	# a usage error (bad params, or precision)
	except SystemExit as e:
		
		print()
		print(e)
		print()
	
	# other ???
	except Exception as other_exception:
		
		print()
		print(other_exception)
		print()

	finally:
		
		# print goodbye
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("+                       Program will terminate now...                            +")
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("\n")
		