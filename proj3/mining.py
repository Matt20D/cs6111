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




def get_frequency_counts(datafile, combinations, iteration):
	''''

	returns: frequency dict of all item sets in combinations

	:param datafile: name of csv file to read data from.
	:param combinations: set of combinations to calculate frequency for

	'''
	# list_combos = list(combinations)

	# this list will store a set version as well as a tuple version
	list_of_combos = list()
	for combo in combinations:
		combo_set = set(combo)
		list_of_combos.append((combo_set, combo))

	print('NUMBER OF COMBINATIONS TO GO THROUGH')
	print(len(list_of_combos))

	freq_counts = defaultdict(int)
	with open(datafile) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")
		num_transactions = 0

		 # track frequency of item
		for row in csv_reader:
			if num_transactions == 0:
				# print("colnames: {}".format(row))
				pass
			else:				
				# print("{}) {}".format(num_transactions, row))
				# print('\n')
				
				#NOTE: should we try and process the whole database so it's a list of sets? 
				# So we don't have to keep doing this conversion?

				row_set = set(row) # convert row to set for easy lookup
				for combo in list_of_combos:
					if combo[0].issubset(row_set):
						freq_counts[combo[1]] += 1				

			num_transactions += 1
	
	return freq_counts


def get_frequent_items(itemset, num_transactions, min_sup):
	'''

	returns: frequency dictionary of itemsets that meet min_sup

	:param itemset: frequency dictionary of items
	:param num_transactions: length of input file
	:param min_sup: minimum frequency the itemset needs to meet)

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
	# 2) delete itemsets that contain subsets that did not occur in the previous iteration
	
	Ck = set()

	for c in Ck:
		k_minus_1_subsets = combinations(c,len(c)-1)
		for s in k_minus_1_subsets:
			if s not in Lk.keys():
				Ck.remove(c)
				break


	return Ck

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

	starting_freq = defaultdict(int) # dictionary to track starting frequencies
	print('Working on iteration 1...')
	with open(datafile) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")
		num_transactions = 0

		 # track frequency of item
		for row in csv_reader:
			if num_transactions == 0:
				# print("colnames: {}".format(row))
				# print('\n')
				pass
			else:				
				# print("{}) {}".format(num_transactions, row))
				# print('\n')
				for item in row:
					if item != "":												
						starting_freq[item] += 1
			num_transactions += 1

			# temporary break for testing
			# if num_transactions == 6:
			# 	break
	# do first pass to get unique items that also meet min_sup
	# Lk is a frequency dictionary ==> {'item1': 2, 'item3': 3, 'item4': 1, ...}
	num_transactions = num_transactions-1
	print("\tNumber of individual items: {}".format(len(starting_freq.keys())))
	L1 = get_frequent_items(starting_freq, num_transactions, min_sup)
	
	Lk = L1
	# main loop --> create combinations based on iteration number, 
	# stops when reaching max number of items (e.g. if there are 
	# 3 total unique items ==> we want this loop to look at item1, item2, and item3)
	i = 2
	while len(Lk.keys()) > 0:
		print('\nWorking on iteration {}...'.format(i))
		# phase 1: use Lk-1 to generate Lk candidates

		Ck = generate_optimized_combinations(Lk, i)

		Ck = combinations(L1.keys(), i) # creates list of combinations depending on iteration	

					

		# scan database to find frequency for each itemset		
		print('Getting frequency counts...')
		freq_counts = get_frequency_counts(datafile, Ck, i)
		
		
		# filter out items that don't meet min_sup
		print('Checking min_sup...')
		Lk = get_frequent_items(freq_counts, num_transactions, min_sup) 

		# get association rule
		print('Getting association rules...')
		get_association_rules(Lk, num_transactions, min_conf)
						
		i+=1

	# STEP 4: Again, find the significant items based on the support threshold

	# STEP 5: Now, make a set of three items that are bought together based on the significant items from Step 4

	print("\nThere are {} transactions in the csv file,".format(num_transactions))


	# sort frequent_items
	sorted_freq = sorted(FREQUENT_ITEMS.items(), key=lambda x: x[1], reverse=True)

	sorted_conf = sorted(HIGH_CONFIDENCE, key=lambda x: x[1], reverse=True)
	# sort high_confidence
	
	# PRINT RESULTS
	with open("output.txt", "w") as f:
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

	print('Time Taken: {}'.format(end_time-start_time))
		

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
	# except Exception as other_exception:
		
	# 	print()
	# 	print("Exception Error: {}".format(other_exception))
	# 	print()

	finally:
		
		# print goodbye
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("+                       Program will terminate now...                            +")
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("\n")