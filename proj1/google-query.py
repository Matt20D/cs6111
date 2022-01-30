#
# Main Driver for Google Query Relevance Feedback
#

import sys # command line arg parsing

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

# main method
def main():

	# ensure that there are at least 4 command line arguments + the program run name
	if not len(sys.argv) >= 5:
		raise Exception("usage: google-query.py <google api key> <google engine id> <precision> <query>")  
	
	# idk if we can even error check this... 
	api_key     = sys.argv[1]
	engine_id   = sys.argv[2]
	
	# ensure that precision is correct input
	precision   = float(sys.argv[3])
	if precision < 0.0 or precision > 1.0:
		raise Exception("query precision needs to be real valued between 0 and 1")
	
	# create a query list of keywords
	query_list  = list()
	for i in range(4, len(sys.argv)):
		query_list.append(sys.argv[i])
	
	print(api_key)
	print(engine_id)
	print(precision)
	print(query_list)

	# get set of stopwords, to help with query parsing
	# we can move this to another method later on, this was just proof of concept
	stopwords = get_stopwords()


# main driver
if __name__ == "__main__":
	main()
