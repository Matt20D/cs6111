#
# Main Driver for Google Query Relevance Feedback
#

import sys # command line arg parsing

# these libraries come from the below source, check the google_search method
# pip3 install google-api-python-client
import pprint
from googleapiclient.discovery import build # for querying google 


# get list of stopwords from gravano's file saved locally
def get_stopwords() -> set():

	# open the file to parse the stopwords and build a set
	try:
		stopwords = set()
		with open("stopwords.txt", "r") as infile:
			for word in infile:
				clean_word = word.strip()
				stopwords.add(clean_word)	
		infile.close()
		return stopwords
		
	except:
		raise Exception("Error with parsing stopwords.txt file for building stopword set")	

# global variable, store all stopwords
STOPWORDS_SET = get_stopwords()

def is_stopword():
	pass

def stop_word_elimination():
	pass

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
def query_google_search(query: str, eid: str, key: str) -> list():
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
		
		temp_list.append(doc['formattedUrl'])
		temp_list.append(doc['title'])
		temp_list.append(doc['snippet'])

		clean_results.append(temp_list)
	
	#print(clean_results)
	return clean_results

# print the query results for the users
def present_results(queries: list) -> None:
	
	rank = 1
	for query in queries:
		print("Rank " + str(rank))
		rank += 1
		print("URL: {}\nTitle: {}\nDescription: {}\n".format(query[0], query[1], query[2]))

# calculate the precision for a list of queries in a given iteration
def calc_precision(queries: list) -> float:
	
	num_no   	= 0
	num_yes     = 0

	for i in range(0, len(queries)):
		while True:
			user_input = input("Is query {} relevant? [y/n] ".format(i+1))
			if user_input.lower() == "y":
				num_yes += 1

				# this is where we need to implement some strategy to determine what words to add to next query

				break
			elif user_input.lower() == "n":
				num_no += 1
				break
			else:
				print("Bad input, please redo...")

	precision = (num_yes) / (num_yes + num_no)
	print(precision)
	return precision

# main method
def main():

	# ensure that there are at least 4 command line arguments + the program run name
	if len(sys.argv) < 5:
		raise Exception("usage: google-query.py <google api key> <google engine id> <precision> <query>")  
	
	# idk if we can even error check this... 
	api_key     = str(sys.argv[1])
	engine_id   = str(sys.argv[2])
	
	# ensure that precision is correct input
	precision_at_k   = float(sys.argv[3])
	if precision_at_k < 0.0 or precision_at_k > 1.0:
		raise Exception("query precision needs to be real valued between 0 and 1")
	
	# create a query list of keywords
	query_list  = list()
	for i in range(4, len(sys.argv)):
		query_list.append(sys.argv[i])
	
	# for debugging
	#print("======")
	#print(api_key)
	#print(engine_id)
	#print(precision_at_k)
	#print(query_list)
	#print("======")

	# execute query
	initial_query = query_google_search(query_list, engine_id, api_key)

	# edge case 1: ensure that there are 10 results on first search
	if len(initial_query) < 10:
		print("Query was not ambiguous, there were less than 10 results in iteration 1")
		quit()
	
	# set up counter for iterations
	num_searches = 1

	# present results
	print("Query Number: " + str(num_searches))
	print("Searched for: " + to_string(query_list) + "\n")
	present_results(initial_query)

	# prompt user for relevance and calculate the initial precision@k value
	precision_k_actual = calc_precision(initial_query)

	# run this loop until we hit the target precision
	while True:

		# edge case 2: I believe this only matters for the first iteration
		if precision_k_actual == 0:
			print("precision @ 10 for query {} is 0".format(num_searches))
			break

		# edge case 3: if we have hit the target precision, then we can terminate.
		elif precision_k_actual >= precision_at_k:
			print("current precision {:.2f} >= target precision {:.2f}. We are done...".format(precision_k_actual, precision_at_k))
			break

		# this is the actual point of the assignment, this is the algorithm we need to develop
		else:
			print("Need to run the actual algorithm now ...")
			print("Put actual algo here!!!!!!")

			#
			# alter the query here, for next loop
			#

			# increment the iteration counter
			num_searches += 1

			# obvi delete later on
			break
	
	# return from main
	return

# main driver
if __name__ == "__main__":

	# print greeting
	print("Welcome to Relevence Feedback Query Optimizer")
	print("Written by Matt Duran and Ethan Garry\n")

	# run the program
	main()

	# print goodbye
	print("Program will terminate now...\n")

"""
Main Algorithm Idea:

1) receive user query as input (list of words), and precision target for the fraction of relevant queries out of top 10 results
	[DONE, with input error checking as well]
2) retrieve top 10 results from google, using google API default values ...
	If there are fewer than 10 results then terminate in first iteration [DONE, and implemented the edge case in this bullet]
3) present results to user, and get relevence feedback for the pages w.r.t. query meaning.
	display title, URL, and description returned by Google. [DONE]
	Needs to be exact top 10 results returned by Google. Do not modify the default vals for search params [DONE]
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

techniques to use:
	stopword elimination

"""
