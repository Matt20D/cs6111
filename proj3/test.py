
from enum import unique
import sys
import csv
from collections import defaultdict
from itertools import combinations
from tracemalloc import start


temp = [1, 2, 3, 4]

row_set = [1,2,3]


combos = combinations(temp,2)



for c in combos:
    print(set(c))
    print(set(c).issubset(row_set))

Row_Set = {'8:20pm', 'Low_Connected_Home_Broadband', '<70%_mobile_boradband', '26%-50%_of_class_FAILED_TEST', '26%-50%_college_career', 'M', '81%-90%_attend_rate', 'Low_percent_blocks_without_commercial_fiber', 'No_Free_Public_wifi', '61%-70%_grad_rate', 'High school', 'Lower East Side', 'Common Core Algebra', '21%-30%_poor_percentage', '0%-10%_of_class_ABOVE_80', '20%-40%_foreign_born', '50k-70k_pop', 'Orchard Collegiate Academy', '11%-20%_underbanked', '<50k_median_sal', '2018', 'General Academic', '3:55pm', '<10%_unbanked', '0-20_bus_routes', '<50%_mobile_broadband', '60-69_mean_score', '<300_student_school', '1-5_subway_stops', 'Low_Connected_Mobile_Broadband', '1-5_AP_CLASSES', '10 public_computer_centers', '>10%_unemployment', '>50%_of_class_PASSED_TEST', '01M292', '0-25_total_transit_ways'}

Combo =  {'01M292', 'M'}

print(Combo.issubset(Row_Set))

test = [1,2 ,3 ,4]

copy = test.remove(2)
print(copy)
print(test)