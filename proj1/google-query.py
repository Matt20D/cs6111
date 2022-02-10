#
# Main Driver for Google Query Relevance Feedback
#

# Library Modules Needed
from operator import inv
import sys # command line arg parsing
import numpy as np # havent decided which one yet
import pandas as pd # havent decided which one yet
import re # regex
import pprint # printing out Datastructures in a readable format
import math # for logs
import Tokenizer # class written to execute get request and get the keywords back
import requests

from googleapiclient.discovery import build # for querying google 


# use this method to print all relevant parameters to the console
def print_params(api_key, eid, precision, precision_calc, query, iteration):
	
	print("+++++++++++++++++++++++++++++++++++++++++++++++++")
	print(" Client Key  			= {}".format(api_key))
	print(" Engine Key  			= {}".format(eid))
	print(" Desired Precision		= {}".format(precision))
	print(" Calculated Precision		= {}".format(precision_calc))
	print(" Query       			= {}".format(to_string(query)))
	print(" Iteration   			= {}".format(iteration))
	print("+++++++++++++++++++++++++++++++++++++++++++++++++")
	print()

# convert the query list of keywords to a string
def to_string(query_l: list) -> str:
	query_s = ""
	for i in range (0, len(query_l)):
		query_s += query_l[i]
		if i != len(query_l) - 1:
			query_s += " "
	return query_s

# for a particular iteration, lets pass in the correct parameters to execute a google query
"""
params
q/query: query input list
cx/eid:  search engine id
key: 	 google API key
"""
def query_google_search(query: list, eid: str, key: str) -> list():
	# source: https://github.com/googleapis/google-api-python-client/blob/main/samples/customsearch/main.py
	service = build("customsearch", "v1",
		developerKey=key)

	res  = service.cse().list(
			key = key,
			cx = eid,
			q  = to_string(query)
			).execute()

	# print out the whole JSON response document from google engine
	#print(res)	
	#pprint.pprint(res)

	# get the actual queries from response document, max of 10 returned always
	queries = res['items']

	#pprint.pprint(queries)
	#print(len(queries))

	# lets parse the data thate we need URL, title, desc from the JSON object
	clean_results = []
	for doc in queries:

		temp_list = []
		#pprint.pprint(doc)
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
	
	#print(clean_results)
	return clean_results

def remove_bad_results(queries: list) -> list:
	#print("removing non-html results if they exist...")
	clean_queries = []
	for query in queries:
		if query[3] == 'html-file':
			clean_queries.append(query)
	return clean_queries

# get user input and return True or False
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

# global storage of documents according to label by relevance feedback
RELEVANT_DOCS = []
NON_RELEVANT_DOCS = []

# print the query results for the users,
# ask for relevence feedback, and return the precision metric
def present_results(queries: list) -> float:
	global RELEVANT_DOCS, NON_RELEVANT_DOCS
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
	return precision

# return an inverted list, that contains the term_frequency of each term
# in a given document snippet + title of document
def get_term_frequency(documents: list) -> dict:
	
	# Hash Table with inverted list DS for easier indexing
	inverted_list = {}

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
			print("Http error for {}, we will now just use stored snippet and title".format(doc_url))
			# use the snippet and title to get all keywords via the regex match
			all_keywords = tk.regex_match(doc[1] + " " + doc[2])

		# lets add to the inverted list, essentially creating our own linked list on hash table
		# each word will contain a row, of length len(documents). if word exists, find doc location and increment
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

def convert_to_dataframe(inv_list: dict, is_relevant: bool) -> pd.DataFrame: # return a PD DataFrame

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

def do_log_term_frequency(data:pd.DataFrame) -> pd.DataFrame:
	# get a deep copy so we do not modify the tf dataframe
	data_copy = data.copy(deep=True)
	return data_copy.applymap(lambda x: 0 if x == 0 else (1 + math.log(x, 10)))

def mult_tf_idf(row):
	# each cell * last val in col (the idf weight)
	for i in range(0, len(row)-1):
		row[i] = row[i] * row[len(row)-1]
	return row

def calc_idf(row: list) -> float:
	document_frequency = 0
	for cell in row:
		if cell > 0:
			document_frequency += 1
	x = len(row) / document_frequency
	return math.log(x, 10)

# remember idf weights how rare a term is across documents
# multiply that weight by how frequent the term is within a document
# tf-idf weights are used to help us pick the most relevant words
def do_tf_idf(data:pd.DataFrame) -> pd.DataFrame:

	# get a deep copy so we do not modify the tf dataframe
	data_copy = data.copy(deep=True)

	# calc idf_weights using formula from slides
	# math.log(x,10) where x = N / document frequency
	# so for each word, we will get the inverse document frequency meaning
	# lets see out of how many documents, this word shows up in.

	# faster than iterrows()
	# https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
	idf_weights = [calc_idf(row) for row in data_copy[data_copy.columns].to_numpy()]
		
	# initialize a column to store the idf weight
	data_copy["word_idf_weight"] = idf_weights
		
	# now multiply tf * idf to get the final weight
	new_data = data_copy.apply(mult_tf_idf, axis=1)
	
	# drop the column
	new_data = new_data.drop(columns=["word_idf_weight"])
	
	return new_data

# emphasize the location of certain words by title (most weight), and snippet
# which is the early part of the document (2nd most weight)
def apply_word_zone_heuristic(colname: str, keyword: str, word_value: float) -> float:
	weights = {'title':  1.20, 'snippet': 1.10}

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

# this method will score a document's relevance for a query
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

# this method will score all of the relevant documents and return
# them in sorted order
def score_rel_docs(query: list, rel_docs: pd.DataFrame) -> list:
	all_scores = []
	for columnName, columnData in rel_docs.iteritems():
		curr_score = score(query, columnData)
		all_scores.append( (columnName, curr_score) )
	all_scores.sort(key=lambda x: x[1], reverse=True)
	return all_scores

# google heuristic
# figure out a way to work in google's ranking, to the weighting scheme, only a round by round basis
# R_Doc_1 >>  R_Doc_2 >>  ... >> R_Doc_10. Only slightly tho, we will use googles' work that they have done
# with implementing their search engine and ranking scheme.
def apply_google_heuristic(documents: list[tuple]) -> list[tuple]:
	new_ranking = []
	weights = {'R_Doc_1':  1.00, 'R_Doc_2': 0.95, 'R_Doc_3': 0.90, 
			   'R_Doc_4':  0.85, 'R_Doc_5': 0.80, 'R_Doc_6': 0.75,
			   'R_Doc_7':  0.70, 'R_Doc_8': 0.65, 'R_Doc_9': 0.60, 
			   'R_Doc_10': 0.55
			  }
	for document in documents:
		new_weight = document[1] * weights[document[0]]
		new_ranking.append( (document[0], new_weight) )

	# sort and return the weighted ranking
	new_ranking.sort(key=lambda x: x[1], reverse=True)

	return new_ranking

# here will try and pick the best words so that we can begin to augment
# the query. Return a list of words, to be added to the queries and then tested.
def choose_words(scores: list[tuple], data: pd.DataFrame, query: list) -> list:	
	words = set() # get 12 words max
	max_words = 20

	# scale max per doc
	if len(scores) == 1:
		max_per_doc = max_words
	else:
		max_per_doc = 10
	
	# go from highest ranked doc to lowest ranked doc
	for document in scores:

		# track number of added for a document
		added = 0

		# get col vector and sort in desc
		vec = data[document[0]].sort_values(ascending=False)
		
		# go through all of the nonzero words in doc vector
		for index, value in vec.items():
			
			# we have reached our limit of max_words
			if len(words) == max_words:
				break

			# we have hit a weight of 0
			# or we have the max number of words from document
			# lets move on to next doc
			if max_per_doc == added or value == 0:
				break

			# ensure that the word is not like any others in query
			# hack for word stemming
			in_query = False
			for word in query:
				if (index in word) or (word in index):
					in_query = True
					break
			
			# completely new unique word
			if not in_query:
				# add word and increment doc counter
				words.add(index)
				added += 1
		
		# we have reached our limit of max_words
		if len(words) == max_words:
			break
	
	# what happens if the words set contains 0? We should choose one randomly
	# IDK if this is a case that needs to be tested.
	return words

# using all of the keyword rankings lets build all of the combinations of the old
# query terms + one new term, or old query terms + two new terms.
# at a max this should return 210 potential queries. (based off the numbers in choose words)
def generate_queries(curr_query: list, potential_words: set) -> list:

	len_one = set() # should equal 20 max.
	len_two = set() # 190 should be max. 20 choose 2 == 190
	
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
	
	# at max there should be 210 potential query lists
	all_combos = []

	# concatenate one word to previous query keyword list
	for word in len_one:
		temp_list = [word]
		temp_list = curr_query + temp_list
		all_combos.append(temp_list)

	# concatenate two words to previous query keyword list
	for word in len_two:
		temp_list = [word[0], word[1]]
		temp_list = curr_query + temp_list
		all_combos.append(temp_list)

	return all_combos

# This method will return the new string, which hopefully produces better results for
# the relevance feedback
# This is the bulk of the assignemnt, we will run all augmentation out of here.
def run_augmentation(curr_query: list) -> list: # return a list of keywords, after potentially adding at max 2 new
	global RELEVANT_DOCS, NON_RELEVANT_DOCS
	
	#
	# Query Data Structures and weights
	#

	# keep the labeled documents separate, but calculate term frequency for both
	inverted_list_relevant     = get_term_frequency(RELEVANT_DOCS)
	#inverted_list_non_relevant = get_term_frequency(NON_RELEVANT_DOCS) # not using irrelevant docs

	# create a pandas dataframe for the document vectors
	relevant_vectors = convert_to_dataframe(inverted_list_relevant, is_relevant=True)
	#non_relevant_vectors = convert_to_dataframe(inverted_list_non_relevant, is_relevant=False) # not using irrelevant docs

	# do log term frequency for each of the numbers in the dataframe, we want rarer terms to be more valuable
	rel_log_tf = do_log_term_frequency(relevant_vectors)
	#non_rel_log_tf = do_log_term_frequency(non_relevant_vectors) # not using irrelevant docs

	# this step will calculate the tf-idf weights
	rel_tf_idf     = do_tf_idf(rel_log_tf)
	#non_rel_tf_idf = do_tf_idf(non_rel_log_tf) # not using irrelevant docs
	#print(rel_tf_idf)

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
		print("in case 1")
		
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
		print("in case 2")

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
	# Step 3: test the new queries using rocchios algo, and use the highest one
	#
	
	# if len(curr_query) == 1 or len(rel_log_tf.columns) == 1:
		# normalize rel_log_tf
		# use rocchio's algo for normal vectors and all potential queries
		# choose the best query that is clustered the best
	# else:
		# normalize rel_log_tf
		# use rocchio's algo for normal vectors and all potential queries
		# choose the best query that is clustered the best

	# return new query as a list


	# reset the relevent docs, lets only consider this iteration's pool of 
	# relevent v non-relevent docs
	RELEVANT_DOCS     = None
	NON_RELEVANT_DOCS = None

	# obviously this becomes the new query ...
	return "UNDER CONSTRUCTION".split()

#
# Log file stuff, This is useful for final steps
#

# use this for serializing our data
def make_json(iter_num: int, curr: str, prec: float, res: list) -> dict:

	json = {"iter": iter_num, \
			"query string": curr, \
			"precision": prec, \
			"google results": res}

	return json

# use this for logging to file later
def log_iteration() -> None:
	pass

#
# main method, do all of the dirty work
#
def main():

	# ensure that there are at least 4 command line arguments + the program run name
	if len(sys.argv) > 5:
		raise Exception(" usage: google-query.py <google api key> <google engine id> <precision> <query>")  
	
	# idk if we can even error check this... 
	api_key     = str(sys.argv[1])
	engine_id   = str(sys.argv[2])
	
	# ensure that precision is correct input
	precision_at_k   = float(sys.argv[3])
	if precision_at_k < 0.0 or precision_at_k > 1.0:
		raise Exception(" Query precision needs to be real valued between 0 and 1")
	
	# create a query list of keywords
	initial_query 		= sys.argv[4]
	initial_query       = initial_query.split() 
	
	# track all of our queries by iteration
	ALL_QUERIES = {}

	# set up counter for iterations
	num_searches = 1

	# store the intermediate results
	query_results = None

	# current query
	current_query = initial_query

	# run this loop until we hit the target precision
	while True:
		
		# RUN INITIAL QUERY
		if num_searches == 1:

			# print the params to the console
			print_params(api_key, engine_id, precision_at_k, "N/A", initial_query, num_searches)

			# execute query
			query_results = query_google_search(initial_query, engine_id, api_key)

			# edge case 1: ensure that there are 10 results on first search
			if len(query_results) < 10:
				print(" Query was not ambiguous, there were less than 10 results in iteration 1")
				#quit()
				break # break out of loop, and terminate program gracefully

		# do all other queries post modification
		elif num_searches > 1:
			
			# print the params to the console, current_query has been modified from iteration num_searches - 1
			print_params(api_key, engine_id, precision_at_k, precision_k_actual, current_query, num_searches)

			# execute query
			query_results = query_google_search(current_query, engine_id, api_key)

			#TODO delete the break statement (for actual augmentation runs)
			#print("\n Iteration number " + str(num_searches))
			break

		#
		# Remove Non-html files from the query results, if they exist
		#
		query_results = remove_bad_results(query_results)

		# prompt user for relevance and calculate the initial precision@k value
		precision_k_actual = present_results(query_results)
	
		# Logging Purposes
		# add to the ALL_QUERIES data structure, we can use this for logging to a log file later
		ALL_QUERIES[num_searches] = make_json(num_searches, current_query, \
									 		  precision_k_actual, query_results)
		
		# pprint package does a good job of formatting print, check it out
		#pprint.pprint(ALL_QUERIES)

		# edge case 2: I believe this only matters for the first iteration
		if precision_k_actual == 0:
			print(" precision @ 10 for query {} is 0".format(num_searches))
			break

		# edge case 3: if we have hit the target precision, then we can terminate.
		elif precision_k_actual >= precision_at_k:
			print(" current precision {:.2f} >= target precision {:.2f}. We are done...".format(precision_k_actual, precision_at_k))
			break

		# this is the actual point of the assignment, this is the algorithm we need to develop
		# The precision didn't pass our pre-defined target, so lets augment the query using
		# heuristics. Then, set current_query up for the next loop iteration.
		else:
			print(" current precision {:.2f} < target precision {:.2f}. Let's augment...".format(precision_k_actual, precision_at_k))
			#
			# Modify current query, for next loop using algo
			#

			# this function will be the entry point into getting a new query string for 
			# next iteration. Pass the old query keywords, and receive a new one from heuristic analysis
			augmented_query = run_augmentation(current_query)
			current_query = augmented_query
 
			# increment the iteration counter
			num_searches += 1

			# obvi delete later on
			#break
	
	# return from main
	return

# main driver
if __name__ == "__main__":

	# print greeting
	print("+++++++++++++++++++++++++++++++++++++++++++++++++")
	print("+ Welcome to Relevence Feedback Query Optimizer +")
	print("+ Written by Matt Duran and Ethan Garry         +")
	print("+++++++++++++++++++++++++++++++++++++++++++++++++")

	# run the program
	try:
		main()
	except KeyboardInterrupt:
		print("\n")
	finally:
		# print goodbye
		print("+++++++++++++++++++++++++++++++++++++++++++++++++")
		print("+ Program will terminate now...                 +")
		print("+++++++++++++++++++++++++++++++++++++++++++++++++")
		print("\n")

"""
Main Algorithm Idea:

4) calculate precision@10
	if precision@10 greater than target value, then terminate. [DONE]
	elif precision@10 == 0, then terminate. [DONE]
	else: use pages marked as relevant to automatically derive new words that are likely to identify more relevant pages	
	At this point no more user input...!!!

	NOTE 1: Cannot delete any words from the original query, or from the query from the previous iteration. Only add words, at most
	we can introduce at most 2 new words during each round.
	
	NOTE 2: order of words expanded in query is important. Program should automatically consider alternate ways of ordering the words
	in a modified query, and pick the order estimated to be the best. In each iter we can reorder all words, new and old, but cannot
	delete any words.

5) Modify current user query using notes in part 4, to put the keywords in the best possible order. and then go to step 2.

key point: step 4 will need to be fleshed out as much as possible. we can use techniques borrowed from research literature, we 
just need to ensure that we cite any publication.

"""
