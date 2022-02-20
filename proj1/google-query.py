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
import sys # command line arg parsing
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
def print_params(api_key, eid, precision, precision_calc, query, iteration, k) -> None:
	
	print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
	print(" Client Key  			= {}".format(api_key))									
	print(" Engine Key  			= {}".format(eid))
	print(" Desired Precision		= {}".format(precision))
	print(" Calculated Precision@{}	= {}".format(k, precision_calc))
	print(" Query       			= {}".format(to_string(query)))
	print(" Iteration   			= {}".format(iteration))
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

		temp_list = []

		# link has the http/https format which is needed for get request
		temp_list.append(doc['link']) # changed from doc['formattedUrl']
		temp_list.append(doc['title'])
		temp_list.append(doc['snippet'])
		
		# mark whether the doc is html or not in precision counting.
		if 'fileFormat' in doc.keys():
			temp_list.append(doc['fileFormat'])
		else:
			temp_list.append("html-file")

		clean_results.append(temp_list)
	
	return clean_results

"""
desc: 
if a file has been marked as non-html in query_google_search then 
we will simply remove that document result from the list and return
the new clean list
"""
def remove_bad_results(queries: list) -> list:
	#print("removing non-html results if they exist...")
	clean_queries = []
	for query in queries:
		if query[3] == 'html-file':
			clean_queries.append(query)
	return clean_queries

"""
desc: 
method that will prompt user with a question in order
to get their relevance feeback. There is some param checking
to ensure that a 'y' or 'n' is entered. Returns True for 'y' 
and False for 'n'
"""
def get_feedback() -> bool:
	# normal case this loop runs once, but you need
	# to get good input, i.e. a 'y' or 'n'
	while True:
		user_input = input(" Is query relevant [y/n]? ")
		if user_input.lower() == "y":
			return True
		elif user_input.lower() == "n":
			return False
		else:
			print(" Bad input, please redo...")

"""
desc:
Global storage of documents. These lists will be appended to when they are
labeled by relevance feedback, for a given iteration. We are also storing 
words for NLP N-Gram analysis for word ordering.
"""
RELEVANT_DOCS = []
NON_RELEVANT_DOCS = []
N_GRAM_MASTER_LIST = []
WORD_COUNT = defaultdict(int)

"""
desc: present the query results for the users and then 
ask them for their relevance feeback for the particular query.
Also, will store the word count for the title/snippet in the b
N Gram Master List

This method returns the precision@k metric, and the k value for number
of documents considered.
"""
def present_results(queries: list) -> tuple:
	global RELEVANT_DOCS, NON_RELEVANT_DOCS, N_GRAM_MASTER_LIST, WORD_COUNT
	# track query rank
	rank = 1

	# track relevence
	num_no  = 0
	num_yes = 0

	# display query and ask for relevence
	for query in queries:

		# present the query rank
		print(" Rank " + str(rank))
		rank += 1
		
		# present query result to user
		print(" URL: {}\n Title: {}\n Description: {}\n".format(query[0], query[1], query[2]))

		# add description and title to N_GRAM_MASTER list
		# putting breaks in between		
		list_of_title = query[1].split()
		for word in list_of_title:
			WORD_COUNT[word.lower()] += 1
			N_GRAM_MASTER_LIST.append(word.lower())
		N_GRAM_MASTER_LIST.append(" ")

		list_of_descr = query[2].split()
		for word in list_of_descr:
			WORD_COUNT[word.lower()] += 1
			N_GRAM_MASTER_LIST.append(word.lower())
		N_GRAM_MASTER_LIST.append(" ")
		
		# ask user if this query is relevant
		if get_feedback() == True:
			num_yes += 1
			RELEVANT_DOCS.append(query) # This has been labeled by user as relevant
		else:
			num_no += 1
			NON_RELEVANT_DOCS.append(query) # This has been labeled by user as non-relevant

		print("\n")

	# calc and return the precision
	precision = (num_yes) / (num_yes + num_no)
	
	return (precision, (num_yes + num_no))

"""
desc:
return an inverted list, containing the term_frequency of each term
in a given document snippet/title of document
"""
def get_term_frequency(documents: list) -> dict:
	global N_GRAM_MASTER_LIST, WORD_COUNT
	
	print("getting term frequency...")

	# Hash Table with inverted list DS for easier indexing
	inverted_list = {}

	# track all word orderings seen
	# inverted_list_positions = {}

	# of the relevant documents, lets parse the contents of it to build an inverted list data structure
	for i in range(0, len(documents)): # start with indexing just one of them
		doc = documents[i]
		docname = "document_" + str(i)

		#
		# Generate Token keywords for this document
		#

		# get stored url for this document
		doc_url      = doc[0]
		
		#instantiate tokenizer object
		tk           = Tokenizer.Tokenizer(doc_url)

		# try to execute get request
		try:
			# use method to execute get request and return clean document words in list
			all_keywords = tk.get_words()
		
		# on failure just use the snippet and title
		except requests.exceptions.HTTPError:
			#print("Http error for {}, we will now just use stored snippet and title".format(doc_url))
			# use the snippet and title to get all keywords via the regex match			
			all_keywords = tk.regex_match(doc[1] + " " + doc[2])

		# lets add to the inverted list, essentially creating our own linked list on hash table
		# each word will contain a row, of length len(documents). if word exists, find doc location and increment
	
		# for calculating N-gram probability we need the count of every word and the sequence in which we traverse for each document
		for word in tk.all_words:						
			WORD_COUNT[word] += 1
			N_GRAM_MASTER_LIST.append(word)		
	
		# put a break between documents
		N_GRAM_MASTER_LIST.append(" ")
		# print("Length of master list")
		# print(len(N_GRAM_MASTER_LIST))

		for word in all_keywords:						
			if word in inverted_list:
				# find the keyword, then find the document location, increment value
				inverted_list[word][i] += 1
			else:
				# create room for each of the documents in the relevant pool
				# we found a completely new word
				inverted_list[word]    = [0] * len(documents)
				inverted_list[word][i] = 1 # ensure that the value for this word begins at 1

	return inverted_list

"""
desc:
convert an inverted list into a dataframe so we can manipulate document vectors
in a much easier fashion
"""
def convert_to_dataframe(inv_list: dict, is_relevant: bool) -> pd.DataFrame: # return a PD DataFrame
	print("converting to data frame")
	df = pd.DataFrame()
	#df["keyword"] = pd.Series([], dtype="string") # initialize a column

	if is_relevant:
		colnames = []
		for i in range(0,len(RELEVANT_DOCS)):
			colname = "R_Doc_" + str(i + 1)
			df[colname] = pd.Series([], dtype="float") # initialize a column
	else:
		colnames = []
		for i in range(0,len(NON_RELEVANT_DOCS)):
			colname = "NR_Doc_" + str(i + 1)
			df[colname] = pd.Series([], dtype="float") # initialize a column, specify a datatype
	
	# lets add rows to the dataframe
	row_names = {}
	for key in inv_list.keys():
		
		# get the keyword freq in all relevant docs
		key_frequencies = inv_list[key]

		# add row to the end of the dataframe
		#df.loc[len(df)] = [key] + key_frequencies
		row_names[len(df)] = key
		df.loc[len(df)] = key_frequencies

	# set the row indexes with the keyword names
	df = df.rename(index=row_names)

	return df 

"""
desc: 
helper function that applies the log_tf formula 
we learned in class to each cell in the dataframe
"""
def do_log_term_frequency(data:pd.DataFrame) -> pd.DataFrame:
	# get a deep copy so we do not modify the tf dataframe
	data_copy = data.copy(deep=True)
	return data_copy.applymap(lambda x: 0 if x == 0 else (1 + math.log(x, 10)))

"""
desc:
helper function to multiply idf by each tf in the dataframe row
"""
def mult_tf_idf(row):
	# each cell * last val in col (the idf weight)
	for i in range(0, len(row)-1):
		row[i] = row[i] * row[len(row)-1]
	return row

"""
desc:
calculates the idf for a word in a row vector. i.e. the idf of a word
across all of the documents that it shows up in
"""
def calc_idf(row: list) -> float:
	document_frequency = 0
	for cell in row:
		if cell > 0:
			document_frequency += 1
	x = len(row) / document_frequency
	return math.log(x, 10)

"""
desc:
since, idf weights how rare a term is across documents
lets multiply that weight by how frequent the term is within a document
TL;DR: tf-idf weights are used to help us pick the most relevant words

citation: [for using list comprehensions instead of iterrows()]
https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
"""
def do_tf_idf(data:pd.DataFrame) -> pd.DataFrame:
	print("calculating tf-idf weights")
	# get a deep copy so we do not modify the tf dataframe
	data_copy = data.copy(deep=True)

	# calc idf_weights using formula from slides
	# math.log(x,10) where x = N / document frequency
	# so for each word, we will get the inverse document frequency meaning
	# lets see out of how many documents, this word shows up in.

	# faster than iterrows()
	idf_weights = [calc_idf(row) for row in data_copy[data_copy.columns].to_numpy()]
		
	# initialize a column to store the idf weight
	data_copy["word_idf_weight"] = idf_weights
		
	# now multiply tf * idf to get the final weight
	new_data = data_copy.apply(mult_tf_idf, axis=1)
	
	# drop the column
	new_data = new_data.drop(columns=["word_idf_weight"])
	
	return new_data

"""
desc:
heuristic that emphasizes the location of certain words by title (most weight), 
and snippet which is the early part of the document (2nd most weight)
"""
def apply_word_zone_heuristic(colname: str, keyword: str, word_value: float) -> float:

	weights = {'title':  1.50, 'snippet': 1.10} # title should matter much more
	
	# adjust the index to base 0 for array
	doc_index = int(colname[-1]) - 1
	
	# get the stored relevant document
	doc = RELEVANT_DOCS[doc_index]

	# get the title and snippet
	title   = doc[1].lower()
	snippet = doc[2].lower()
	
	# store the new_weight
	new_word_val = word_value 

	# scale up if present in a zone
	if keyword.lower() in title:
		new_word_val *= weights['title']
	
	# we could also potentially not double dip.
	# meaning, if the word has been scaled up, then not multiply also by the snippet weight
	# lets experiment
	if keyword.lower() in snippet:
		new_word_val *= weights['snippet']
	
	return new_word_val

"""
desc:
this helper method will score a document's relevance for a given query.
There is an issue when a query is all stop words, that we never really got 
around to. However, we will end up choosing the best possible words later
on anyways.
"""
def score(curr_query: list, col_vector: pd.Series) -> float:
	score = 0
	for keyword in curr_query:
		# keyword doesnt show up, perhaps was removed as a stopword
		if keyword not in col_vector:
			score += 0
		else:
			# check word zone.
			# if the keyword has been seen in title or snippet scale up, else keep it the same
			score += apply_word_zone_heuristic(col_vector.name, keyword, col_vector[keyword])
	return score

"""
desc:
this method will score all of the relevant documents and return
them in sorted order. Calls the above score() helper for assistance
"""
def score_rel_docs(query: list, rel_docs: pd.DataFrame) -> list:
	all_scores     = []
	for columnName, columnData in rel_docs.iteritems():
		curr_score = score(query, columnData)
		all_scores.append( (columnName, curr_score) )

	# this is a case where the whole query list contains stopwords
	# such as "to be or not to be" or "the who"
	# thus, lets take a simple sum of the column vector.
	# i.e. all docs have a score of 0
	back_up_scores = []
	using_back_up  = False
	if sum([score[1] for score in all_scores]) == 0:
		using_back_up = True
		for columnName, columnData in rel_docs.iteritems():
			col_score = columnData.sum()
			back_up_scores.append( (columnName, col_score) )
	
	# This way, we can at least produce a document ranking for
	# queries composed entirely of stopwords.
	# normally we would be using the 'else' case
	if using_back_up:
		back_up_scores.sort(key=lambda x: x[1], reverse=True)
		return back_up_scores
	else:
		all_scores.sort(key=lambda x: x[1], reverse=True)
		return all_scores

"""
desc:
google heuristic
we wanted to figure out a way to work in google's ranking, to the weighting scheme, only a round by round basis
R_Doc_1 >>  R_Doc_2 >>  ... >> R_Doc_10. Only slightly tho, we will use googles' extensive work that they have done
with implementing their search engine and ranking scheme as a minor heuristics
"""
def apply_google_heuristic(documents: list) -> list:
	new_ranking = []
	weights = {'R_Doc_1':  1.00, 'R_Doc_2': 0.99, 'R_Doc_3': 0.98, 
			   'R_Doc_4':  0.97, 'R_Doc_5': 0.96, 'R_Doc_6': 0.95,
			   'R_Doc_7':  0.94, 'R_Doc_8': 0.93, 'R_Doc_9': 0.92, 
			   'R_Doc_10': 0.91
			  }
	for document in documents:
		new_weight = document[1] * weights[document[0]]
		new_ranking.append( (document[0], new_weight) )

	# sort and return the weighted ranking
	new_ranking.sort(key=lambda x: x[1], reverse=True)

	return new_ranking

"""
desc:
here will try and pick the best words so that we can begin to augment
the query. Return a list of words, to be added to the queries and then tested.
"""
def choose_words(scores: list, data: pd.DataFrame, query: list) -> list:	
	print("choosing words")
	# these are the max number of words to return
	words = set() 
	max_words = 250
	
	# create a max heap so we can compare across all rel docs
	my_heap = []

	# want to use this object to check for stop words, url is not used
	# just want to use the is_stopword check
	tk = Tokenizer.Tokenizer("https://www.google.com/")

	# go from highest ranked doc to lowest ranked doc
	for document in scores:

		# get col vector and sort in desc
		vec = data[document[0]].sort_values(ascending=False)
		
		# go through all of the nonzero words in doc vector
		for index, value in vec.items():
			
			# we have hit a weight of 0, and since they are sorted 
			# there are no more good words
			if value == 0:
				break

			# ensure that the word is not like any others in query
			# hack for word stemming
			in_query = False
			for word in query:
				if (index in word) or (word in index):
					in_query = True
					break
			
			# check if the word is a stopword
			if tk.is_stopword(index):
				#print("skipped stop word")
				continue

			# completely new unique word
			if not in_query:

				# multiply value by one to ensure max heap
				my_heap.append( (-1 * value,index) )
		
		# we have reached our limit of max_words
		if len(words) == max_words:
			break
	
	# O(N) heapify for my max heap
	heapq.heapify(my_heap)
	
	# stop either at 250 words or when my heap is empty
	while max_words > 0 and len(my_heap): 
		new_word = heapq.heappop(my_heap)[1]
		if new_word not in words:
			words.add(new_word)
			max_words -= 1
	
	# what happens if the words set contains 0? We should choose one randomly
	# NOTE: IDK if this is a case that needs to be tested, i dont think so
	if len(words) == 0:
		return {"error"}
	
	# trying to guard against termination on an untested corner case
	else:
		return words

"""
desc:
using all of the keywords that are returned lets build all of the combinations of the old
query terms + one new term, or old query terms + two new terms. This is a combinatorial explosion
but it only hangs the computer for a little while. The final results have been pretty good too.
"""
def generate_queries(curr_query: list, potential_words: set) -> set:
	print("generating queries")
	len_one = set()
	len_two = set()

	# generate all possible combos
	for word in potential_words:
		
		# add one word
		len_one.add(word)
	
		# lets try to add combos of length 2
		for word2 in potential_words:
			
			# dont pair word with itself
			if word == word2:
				continue
			
			# see if the reverse combo is in the set
			if (word2, word) in len_two:
				continue 

			# new combo, add it
			len_two.add((word, word2))
	
	# get all of the new query add ons to score
	# the original words don't matter and they will be constant
	# in the math
	all_combos = len_one.union(len_two)
	return all_combos

"""
desc:
normalize each column vector, by diving each component by the length 
of the whole column vector
"""
def normalize_vectors(data:pd.DataFrame) -> pd.DataFrame:
	
	# get a deep copy so we do not modify the tf dataframe
	data_copy = data.copy(deep=True)

	# work on a column vector one at a time
	for columnName, columnData in data_copy.iteritems():
		
		# square each component of the very long vector and add to the sum
		components_sq = [ x ** 2 for x in columnData]

		# sum all of the components
		col_sum = sum(components_sq)
		
		# take the sqrt of sum of components squared
		col_sum = math.sqrt(col_sum)

		# divide each component by the vector length, therby normalizing
		if col_sum == 0:
			continue
		else:
			# NOTE: can't divide by zero -- likely error only one irrelevant column
			# or could be a bad document
			data_copy[columnName] = data_copy[columnName].map(lambda x: (x * 1.0) / col_sum)
		
	return data_copy

"""
desc: 
cosine similarity is simply the dot product of query list
and the column vectors. I will calculate dot product with all
relevant queries, and then take the average.
This is the most important algorithm here, this is how we get our final query recommendation.
This function will return the new keywords to append to the query stem
"""
def cosine_similarity(rel_data: pd.DataFrame, non_rel_data: pd.DataFrame,  ql: list) -> list:
	
	print(" calculating cosine similarity... ")

	highest_avg_sim = float('-inf') # we want the highest similarity, using all the data
	query_list      = None

	rel_columns     = rel_data.columns
	num_rel_docs    = len(rel_data.columns)
	non_rel_columns     = non_rel_data.columns
	num_non_rel_docs    = len(non_rel_data.columns)

	# for each of the queries
	#print(len(ql))
	for query in ql:
		

		# want to see similar the query is to the current rel and non-rel docs
		temp_sum_rel = [0] * num_rel_docs
		temp_sum_non_rel = [0] * num_non_rel_docs

		# for each keword, go through each relevant document
		# add the weight for the term to the sum in the correct
		# index in temp sum
		for keyword in query:

			# determine how close to relevant documents in current iteration

			# compute dot product with the number of relevant docs
			# where if keyword is present essentially multiply weight by 1.0
			i = 0
			# use a single keyword, and go through all rel docs
			for col in rel_columns:
				
				try:
					temp_sum_rel[i] += rel_data[col][keyword]
				except:
					temp_sum_rel[i] += 0 # this is a stop word, and will be constant across all queries
				i += 1

			# determine how close to non_relevant documents in current iteration
			i = 0	
			for col in non_rel_columns:				
				try:
					temp_sum_non_rel[i] += non_rel_data[col][keyword]
				except:
					temp_sum_non_rel[i] += 0 # this is a stop word, and will be constant across all queries
				i += 1
		
		# lets get the average similiarity to relevant, to push us towards the middle of the cluster
		temp_sum_rel = sum(temp_sum_rel)
		avg_cosine_sim_rel = temp_sum_rel / num_rel_docs

		# lets get the average similiarity to non relevant docs, to push us towards the middle of the cluster
		temp_sum_non_rel = sum(temp_sum_non_rel)
		avg_cosine_sim_non_rel = temp_sum_non_rel / num_non_rel_docs
		
		# rocchio metric
		# use all of the information to score this query
		rocchio = (1.0 * avg_cosine_sim_rel) - (1.25 * avg_cosine_sim_non_rel)

		# what happens on divide by zero
		# if the avg similarity is better than what we have seen so far
		if  rocchio > highest_avg_sim:
			query_list = query # set
			highest_avg_sim = rocchio
			# NOTE: uncomment to see how the winner changes over time
			#print(query_list)
			#print(highest_avg_sim)

	return list(query_list)

"""
desc:
calculates n_gram probability using section 3.1 from the following paper:
		
citation:
https://web.stanford.edu/~jurafsky/slp3/3.pdf
"""
def calc_n_gram(query):

	global N_GRAM_MASTER_LIST, WORD_COUNT
	# print(WORD_COUNT)

	# first check to make sure each word is in word count - if not, raise exception
	for word in query:
		if word not in WORD_COUNT.keys():
			raise Exception(word + ": not found in WORD_COUNT.")


	print(" calculating n_gram probabilities for", query, "...")
	list_of_query_perms = list(itertools.permutations(query))
	bi_gram_occurances = {}

	most_likely_sequence = list(list_of_query_perms[0])
	most_likely_sequence_score = 0	

	if len(query)>1:
		for test_query in list_of_query_perms:
			# print('---------------')
			# print('testing query: ', test_query)
			n_gram_probability = 1
			for i in range(len(test_query)-1):
				word1 = test_query[i].lower()
				word2 = test_query[i+1].lower()
				combo = word1 + word2

				# calculate number of occurances word 1 occurs after word 2 in all docs			
				
				if combo not in bi_gram_occurances.keys():
					bi_gram_occurances[combo] = 0
					for i in range(len(N_GRAM_MASTER_LIST)-1):						
						if N_GRAM_MASTER_LIST[i] == word1 and N_GRAM_MASTER_LIST[i+1] == word2:
							bi_gram_occurances[combo] += 1			

				
				# print('WORD', word1)
				if bi_gram_occurances[combo] == 0:
					bi_gram_occurances[combo] = .001
					
				bi_gram_prob = bi_gram_occurances[combo]/WORD_COUNT[word1]
				# print('bi-gram probability for: ', word1, word2, ' = ', bi_gram_prob)
				n_gram_probability *= bi_gram_prob

			if n_gram_probability > most_likely_sequence_score:
				most_likely_sequence_score = n_gram_probability
				most_likely_sequence = list(test_query)

			# print("n-gram-probability = ", n_gram_probability)
			# print('----------------------')
	
	# print(most_likely_sequence)	
	return most_likely_sequence

"""
desc:
This method will return the new string, which hopefully produces better results for
the relevance feedback. This is the bulk of the assignemnt, we will run all query
augmentation out of here.
"""
def run_augmentation(curr_query: list) -> list: # return a list of keywords, after potentially adding at max 2 new
	global RELEVANT_DOCS, NON_RELEVANT_DOCS, N_GRAM_MASTER_LIST, WORD_COUNT
	
	#
	# Query Data Structures and weights
	#
	

	# keep the labeled documents separate, but calculate term frequency for both
	inverted_list_relevant     = get_term_frequency(RELEVANT_DOCS)
	inverted_list_non_relevant = get_term_frequency(NON_RELEVANT_DOCS)

	# create a pandas dataframe for the document vectors
	relevant_vectors = convert_to_dataframe(inverted_list_relevant, is_relevant=True)
	non_relevant_vectors = convert_to_dataframe(inverted_list_non_relevant, is_relevant=False)

	# do log term frequency for each of the numbers in the dataframe, we want rarer terms to be more valuable
	rel_log_tf = do_log_term_frequency(relevant_vectors)
	non_rel_log_tf = do_log_term_frequency(non_relevant_vectors)

	# this step will calculate the tf-idf weights
	rel_tf_idf     = do_tf_idf(rel_log_tf)
	non_rel_tf_idf = do_tf_idf(non_rel_log_tf)

	#
	# Query Augmentation
	#

	#
	# Step 1: Score words and find ones that have the highest weights, in different contexts
	#

	# case 1: idf doesnt matter in query with one term, its a scalar applied to all documents
	# just work with the most relevant document and pull the word
	# case 2: if there is only one relevant document, then we cannot use tf-idf weights, becuase it would all be zero
	if len(curr_query) == 1 or len(rel_log_tf.columns) == 1:
		
		# here we will only use the tf dataframes
		# also use the word zone heuristic
		doc_scores = score_rel_docs(curr_query, rel_log_tf)
		
		# apply google heuristic
		doc_scores = apply_google_heuristic(doc_scores)

		# Here is where we choose words
		potential_words = choose_words(doc_scores, rel_log_tf, curr_query)
	
	# since the query has multiple terms, idf actually differentiates term weights among
	# documents in the database
	else:

		# here we will use the tf-idf dataframes
		# also use the word zone heuristic
		doc_scores = score_rel_docs(curr_query, rel_tf_idf)

		# apply google heuristic
		doc_scores = apply_google_heuristic(doc_scores)

		# Here is where we choose words
		potential_words = choose_words(doc_scores, rel_log_tf, curr_query)
	
	#
	# Step 2: use the words to create a bunch of new queries
	#
	
	# try adding one word, and adding two words
	potential_queries = generate_queries(curr_query, potential_words)
	
	#
	# Step 3: test the new queries using cosine similarity, and use the highest one
	#

	# need this check because tf-idf would be 0 for the whole column, if there was only one document
	# Also for one term, there will be no effect, so lets just use term frequency.
	if len(curr_query) == 1 or len(rel_log_tf.columns) == 1 or len(non_rel_log_tf.columns) == 1:
		print(" normalizing tf weights for relevant document vectors ...")
		
		# normalize rel_log_tf and non_rel_log_tf
		rel_docs = normalize_vectors(rel_log_tf)
		non_rel_docs = normalize_vectors(non_rel_log_tf)

	# we have a good cluster of rel to non rel docs, we are good to use tf-idf
	else:
		print(" normalizing tf-idf weights for relevant document vectors ...")
		
		# normalize rel_tf_idf and non_rel_tf_idf
		rel_docs = normalize_vectors(rel_tf_idf)
		non_rel_docs = normalize_vectors(non_rel_tf_idf)
		
	# calculate cosine similarity with and all potential queries and the relevant docs
	# choose the best query that is clustered to the best
	# and want to find most dissimilar to irrelevant
	# cosine_similarity just returns the stem, so concatenate it with the current query
	new_query = curr_query + cosine_similarity(rel_docs, non_rel_docs, potential_queries)
		
	#
	# step 4: last step, work on query ordering. This seems very NLP-y
	try:
		reordered_query = calc_n_gram(new_query)
	except Exception as e:
		print(e)
		reordered_query = new_query

	# reset the relevent docs, lets only consider this iteration's pool of 
	# relevent v non-relevent docs
	RELEVANT_DOCS     	= []
	NON_RELEVANT_DOCS 	= []
	N_GRAM_MASTER_LIST 	= []
	WORD_COUNT 			= defaultdict(int)

	return reordered_query

"""
desc:
main method where program control is run out of.
"""
def main() -> None:

	# ensure that there are at exactly 4 command line arguments + the program run name
	# Query is a string with as many words as desired
	if len(sys.argv) != 5: # changed from ... > 5
		sys.exit(" usage: google-query.py <google api key> <google engine id> <precision> <query>")

	# idk if we can even error check this... 
	api_key     = str(sys.argv[1])
	engine_id   = str(sys.argv[2])
	
	# ensure that precision is correct input
	precision_at_k   = float(sys.argv[3])
	if precision_at_k < 0.0 or precision_at_k > 1.0:
		sys.exit(" usage: Query precision needs to be real valued between 0 and 1")

	# create a query list of keywords
	initial_query 		= sys.argv[4]
	initial_query       = initial_query.split() 

	# set up counter for iterations
	num_searches = 1

	# store the intermediate results
	query_results = None

	# current query
	current_query = initial_query

	# store the precision@<how_many_docs>
	k = 10

	# run this loop until we hit the target precision
	while True:

		# RUN INITIAL QUERY
		if num_searches == 1:

			# print the params to the console
			print_params(api_key, engine_id, precision_at_k, "N/A", initial_query, num_searches, k)

			# execute query
			query_results = query_google_search(initial_query, engine_id, api_key)

			# edge case 1: ensure that there are 10 results on first search
			if len(query_results) < 10:
				print(" Query was not ambiguous, there were less than 10 results in iteration 1")
				break # break out of loop, and terminate program gracefully

		# do all other queries post modification
		elif num_searches > 1:
			
			# print the params to the console, current_query has been modified from iteration num_searches - 1
			print_params(api_key, engine_id, precision_at_k, precision_k_actual, current_query, num_searches, k)

			# execute query
			query_results = query_google_search(current_query, engine_id, api_key)

		#
		# Remove Non-html files from the query results, if they exist
		#
		query_results = remove_bad_results(query_results)

		# prompt user for relevance and calculate the initial precision@k value
		# also store the k value (i.e. precision@<how_many>)
		precision_k_actual, k = present_results(query_results)
	
		# edge case 2: I believe this only matters for the first iteration
		if precision_k_actual == 0:
			print(" precision@{} for query {} is 0".format(k, num_searches))
			print(" Below desired precision, but can no longer augment the query...\n")
			break # break out of loop, and terminate program gracefully

		# edge case 3: if we have hit the target precision, then we can terminate.
		elif precision_k_actual >= precision_at_k:
			print(" current precision@{} {:.2f} >= target precision@{} {:.2f}. We are done...\n".format(k, precision_k_actual, k, precision_at_k))
			break  # break out of loop, and terminate program gracefully

		# this is the actual point of the assignment, this is the algorithm we need to develop
		# The precision didn't pass our pre-defined target, so lets augment the query using
		# heuristics. Then, set current_query up for the next loop iteration.
		else:
			print(" current precision@{} {:.2f} < target precision@{} {:.2f}. Let's augment...".format(k, precision_k_actual, k, precision_at_k))
			
			#
			# Modify current query, for next loop using algo
			#

			# this function will be the entry point into getting a new query string for 
			# next iteration. Pass the old query keywords, and receive a new one from heuristic analysis
			print(" running augmentation algorithm, wait times may vary... ")
			augmented_query = run_augmentation(current_query)
			current_query = augmented_query
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
		print("+                Welcome to Relevence Feedback Query Optimizer                   +")
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
		