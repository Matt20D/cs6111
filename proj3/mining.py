"""
File: mining.py
Description: File which extracts association rules from desired dataset
Authors: Matthew Duran and Ethan Garry
"""

from ast import Del
from enum import unique
import sys
import csv
from collections import defaultdict
from itertools import combinations
from tracemalloc import start
import datetime

FREQUENT_ITEMS = {} # tracks all itemsets that are above a certain min_supp threshold

# list of tuples that tracks all association rules that meet a confidence threshold
# items the form of ==> ([diary] => [pen], 1.0, .75)
# where [diary] => [pen] is a string crafter in get_association rules
# 1.0 is the confidence of the rule
# .75 is support of diary, pen

HIGH_CONFIDENCE = []

# Store the data from the DB file
# list of sets
# where ith element is the ith transaction stored as a set
CSV_DATA = []



def scan_database(combinations: set):
	''''

	returns: frequency dict of all item sets in combinations

	:param datafile: name of csv file to read data from.
	:param combinations: set of combinations to calculate frequency for

	'''
	# list_combos = list(combinations)

	print('\tNumber of combinations to go through: ', len(combinations))	

	# get the support for an itemset
	freq_counts = defaultdict(int)
	
	# scan the data
	for row_set in CSV_DATA:
	
		for combo in combinations:
			if set(combo).issubset(row_set):
				freq_counts[combo] += 1				
	
	return freq_counts


def get_frequent_items(itemset, num_transactions, min_sup):
	'''

	returns: frequency dictionary of itemsets that meet min_sup

	:param itemset: frequency dictionary of items
	:param num_transactions: length of input file - column header
	:param min_sup: minimum support frequency the itemset needs to meet

	'''
	res = {}
	for elem in itemset.keys():		
		if itemset[elem]/num_transactions > min_sup:			
			FREQUENT_ITEMS[elem] = itemset[elem]
			res[elem] = itemset[elem]
	return res

def get_association_rules(high_support_itemsets, num_transactions, min_conf):
	'''
	
	returns: nothing, but adds high_confidence rules to the 
	HIGH_CONFIDENCE list 	

	:param high_support_itemsets: list of items that meet min_sup threshold
	:param num_transactions: number of transactions in the dataset
	:param min_conf: minimum confidence specified by user
	'''

	for itemset in high_support_itemsets:				
		supp_LHS_U_RHS = FREQUENT_ITEMS[itemset]		
		for item in itemset:
			LHS_list = [x for x in itemset if x != item]
			if len(LHS_list) == 1: # tuples are weird with one item
				LHS_tuple = LHS_list[0]
			else:
				LHS_tuple = tuple(LHS_list)

			supp_LHS = FREQUENT_ITEMS[LHS_tuple]
			conf = (supp_LHS_U_RHS / supp_LHS)

			if conf > min_conf:
				LHS = LHS_list
				RHS = item
				assoc_rule = "{} => [\'{}\']".format(LHS, RHS)
				HIGH_CONFIDENCE.append((assoc_rule, conf, supp_LHS_U_RHS/num_transactions))
	return

def generate_optimized_combinations(Lk, iteration):
	'''

	returns: list of combinations for the next iteration
	in a set of tuples more efficiently than brute force

	uses the outline/algorithm specified in secrtion 2.1.1
	http://www.cs.columbia.edu/~gravano/Qual/Papers/agrawal94.pdf

	:param Lk: frequency distribution of previous iterations combinations
	:param iteration: current iteration number 
	
	'''

	#NOTE: this function is comprised of two steps
	
	# 1) join Lk-1 with itself and perform the SQL statement outlined in the paper	
	
	Ck = set()

	if iteration == 2:
		for s in Lk.keys():
			for s2 in Lk.keys():
				if s != s2:													
					list_to_add = [s, s2]															
					tup_to_add = tuple(sorted(list_to_add))					
					Ck.add(tup_to_add)
	else:
		for tup in Lk.keys():
			for tup2 in Lk.keys():
				# SQL optimization for sorting
				# ensure that tup_i_k-1 and tup2_i_k-1 are equivalent 
				# and tup_k < tup2_k 								
				if tup != tup2 and tup[:-1] == tup2[:-1] and tup[-1] < tup2[-1]:									
					new_list = list(tup)
					elem_to_add = tup2[-1]
					new_list.append(elem_to_add)				
					Ck.add(tuple(new_list))				
	
	Ck_before_delete = len(Ck)
	
	# 2) delete itemsets that contain subsets that did not occur in the previous iteration -- the subsets need to be sorted
	new_Ck = set()
	key_set = Lk.keys()
	for c in Ck:
		# print('Checking new combination...')
		add_to_newCk = True		
		for i in range(len(c)):
			subset = c[:i] + c[i+1:]
			# print('Checking subset: ', subset)			
			if len(subset) == 1:
				# first get the intersection between subset and key_set
				# if the intersection != subset, then subset is not a subset LOL
				if subset[0] not in key_set: 
					add_to_newCk = False
					break
			elif subset not in key_set:
				add_to_newCk = False
				break			
		if add_to_newCk:
			new_Ck.add(c)


	print("\tNumber of itemsets pruned: ", Ck_before_delete-len(new_Ck))	
	
	return new_Ck

def main() -> None:

	# ensure proper usage
	start_time = datetime.datetime.now()	

	if len(sys.argv) != 4:
		sys.exit(" usage: mining.py <dataset.csv> <min_sup> <min_conf>")
	
	# parse CL Args
	datafile  = str(sys.argv[1])
	min_sup   = float(sys.argv[2])
	min_conf  = float(sys.argv[3])

	# error check precision vals
	if min_sup < 0.0 or min_sup > 1.0:
		sys.exit("min support needs to be a float between 0 and 1")

	if min_conf < 0.0 or min_conf > 1.0:
		sys.exit("min confidence needs to be a float between 0 and 1")

	# followed tutorial: https://realpython.com/python-csv/ to read the csv
	# in a clean manner. I have used this code before to read other csv's

	#
	# Read in the CSV, and do first pass on it
	#
	starting_freq = defaultdict(int) # dictionary to track starting frequencies
	
	print("Reading data from \'{}\' file".format(datafile))
	with open(datafile) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")
		num_transactions = 0

		 # track frequency of item
		for row in csv_reader:
			
			# this is row 1, i.e the col headers
			if num_transactions == 0:
				# print("colnames: {}".format(row))
				# print('\n')
				
				# essentially skip the col headers
				num_transactions = 1
				#pass
			else:				
				# print("{}) {}".format(num_transactions, row))
				# print('\n')
				for item in row:
					if item != "":												
						starting_freq[item] += 1
				
				# store the row that we read in, so we only touch the data once
				CSV_DATA.append(set(row))

				# increase the row count				
				num_transactions += 1

			# temporary break for testing
			# if num_transactions == 6:
			# 	break
		
		# subtract one to remove column header "transaction"
		num_transactions = num_transactions-1

		# sanity check that the file has data
		if num_transactions <= 0:
			sys.exit("There are 0 transactions in the \'{}\' csv file".format(datafile))
	
	print("\tThere are {} transactions in the \'{}\' file.\n".format(num_transactions, datafile))
	# do first pass to get unique items that also meet min_sup
	# Lk is a frequency dictionary ==> {'item1': 2, 'item3': 3, 'item4': 1, ...}
	print('Working on iteration 1...')
	print("\tNumber of individual items: {}".format(len(starting_freq.keys())))
	
	# get the frequent itemsets that are above min support
	L1 = get_frequent_items(starting_freq, num_transactions, min_sup)
	Lk = L1

	#
	# main loop --> create combinations based on iteration number 
	# terminate when reaching max number of items (e.g. if there are 
	# 3 total unique items ==> we want this loop to look at item1, item2, and item3)
	#

	i = 2
	while len(Lk.keys()) > 0:
		print('\nWorking on iteration {}...'.format(i))
		# phase 1: use Lk-1 to generate Lk candidates

		Ck = generate_optimized_combinations(Lk, i) # this is the optimized implementation

		#Ck = list(combinations(L1.keys(), i)) # creates list of combinations depending on iteration -- this is the basic implementation
				
		# scan database to find frequency for each itemset		
		print('\tGetting frequency counts...')
		freq_counts = scan_database(Ck)
		
		# get the frequent itemsets that are above min support
		# filter out items that don't meet min_sup
		print('\tChecking min_sup...')
		Lk = get_frequent_items(freq_counts, num_transactions, min_sup) 

		# get association rule
		print('\tGetting association rules...')
		get_association_rules(Lk, num_transactions, min_conf)
						
		i+=1


	# sort frequent_items
	sorted_freq = sorted(FREQUENT_ITEMS.items(), key=lambda x: x[1], reverse=True)

	# sort high_confidence
	sorted_conf = sorted(HIGH_CONFIDENCE, key=lambda x: (x[1],x[2]), reverse=True)

	
	# Write results to output.txt

	with open("example-run.txt", "w") as f:
		f.write("==Frequent itemsets (min_sup={}%)\n".format((min_sup*100)))
		for elem in sorted_freq:		
			if isinstance(elem[0], str):				
				f.write("[\'{}\'], {}%".format(elem[0], round(elem[1])*100/num_transactions, 6))
			else:
				f.write("{}, {}%".format(list(elem[0]), round(elem[1]*100/num_transactions, 6)))
			f.write('\n')

		f.write('\n\n')
		f.write("==High-confidence association rules (min_conf={}%)\n".format(min_conf*100))
		for elem in sorted_conf:
			f.write("{}, (Conf: {}%, Supp: {}%)".format(elem[0], round(elem[1]*100, 6), round(elem[2]*100, 6)))			
			f.write('\n')

	end_time = datetime.datetime.now()

	print()
	print('Algorithm Time Taken: {}'.format(end_time-start_time))
		

"""
main driver for the program
"""
if __name__ == "__main__":
	
	try:

		# print greeting
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("+                   Welcome to Data Mining Association Rules                     +")
		print("+                    Written by Matt Duran and Ethan Garry                       +")
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print()	

		# run the program
		main()

	# control-c graceful exit
	except KeyboardInterrupt:
		
		print("\n")
	
	# a usage error (bad params, or precision)
	except SystemExit as e:
		
		print()
		print("SystemExit: " + str(e))
		#print(e)
		print()
	
	# handles exceptions such as error in reading file
	except Exception as other_exception:
		
		print()
		print("Exception Error: {}".format(other_exception))
		print()

	finally:
		
		# print goodbye
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("+                       Program will terminate now...                            +")
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("\n")