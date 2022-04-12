"""
File: mining.py
Description: File which extracts association rules from desired dataset
Authors: Matthew Duran and Ethan Garry
"""

import sys
import csv
from collections import defaultdict


def main() -> None:

	# ensure proper usage
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
	with open(datafile) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")
		line_count = 0

		Ck = defaultdict(int) # track frequency of item
		for row in csv_reader:
			if line_count == 0:
				print("colnames: {}".format(row))
			else:
				print("{}) {}".format(line_count, row))
				for item in row:
					Ck[item] += 1
			line_count += 1

			# temporary break for testing
			if line_count == 5:
				break
		print(Ck)
		# ALGORITHM

		# STEP 1: Create a frequency table of all the items that occur in all transactions

		# STEP 2: Find the significant items based on the support threshold

		# STEP 3: From the significant items, make possible pairs irrespective of the order

		# STEP 4: Again, find the significant items based on the support threshold

		# STEP 5: Now, make a set of three items that are bought together based on the significant items from Step 4

		print("there are {} lines in csv files".format(line_count))

		'''
		Output the frequent itemsets and the high-confidence association rules to a 
		file named output.txt: in the first part of this file, for the frequent itemsets, 
		each line should include one itemset, within square brackets, and its support, 
		separated by a comma (e.g., [item1,item2,item3,item4], 7.4626%). The lines in 
		the file should be listed in decreasing order of their support. In the second 
		part of the same output.txt file, for the high-confidence association rules, each 
		line should include one association rule, with its support and confidence 
		(e.g., [item1,item3,item4] => [item2] (Conf: 100%, Supp: 7.4626%)). The lines 
		in the file should be listed in decreasing order of their confidence.
		'''

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