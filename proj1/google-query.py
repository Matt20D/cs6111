#
# Main Driver for Google Query Relevance Feedback
#

import sys # command line arg parsing
# pip3 install google-api-python-client
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
def query_google_search(query: str, eid: str, key: str):
	# source: https://github.com/googleapis/google-api-python-client/blob/main/samples/customsearch/main.py
	service = build("customsearch", "v1",
		developerKey=key)

	print("made it here\n\n\n\n")
	print("engine_id: " + eid)
	print("key: " + key)
	res  = service.cse().list(
			key = key,
			cx = eid,
			q  = to_string(query)
			).execute()

	print(res)	

# main method
def main():

	# ensure that there are at least 4 command line arguments + the program run name
	if not len(sys.argv) >= 5:
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
	print("======")
	print(api_key)
	print(engine_id)
	print(precision_at_k)
	print(query_list)
	print("======")

	# execute query
	query_google_search(query_list, engine_id, api_key)

# main driver
if __name__ == "__main__":
	main()

"""
Main Algorithm Idea:

1) receive user query as input (list of words), and precision target for the fraction of relevant queries out of top 10 results
2) retrieve top 10 results from google, using google API default values ...
	If there are fewer than 10 results then terminate in first iteration
3) present results to user, and get relevence feedback for the pages w.r.t. query meaning.
	display title, URL, and description returned by Google.
	Needs to be exact top 10 results returned by Google. Do not modify the default vals for search params
4) calculate precision@10
	if precision@10 greater than target value, then terminate.
	elif precision@10 == 0, then terminate.
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


need to use Google Custom Search JSON API for querying google
"""
