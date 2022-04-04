"""
File: mining.py
Description: File which extracts association rules from desired dataset
Authors: Matthew Duran and Ethan Garry
"""

import sys
import csv

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
		for row in csv_reader:
			if line_count == 0:
				print("colnames: {}".format(row))
			else:
				print("{}) {}".format(line_count, row))
			line_count += 1
		print("there are {} lines in csv files".format(line_count))



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