# actual tests

#python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 2 0.7 "bill gates microsoft" 10
# python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 1 0.7 "mark zuckerberg harvard" 10
 python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 2 0.7 "sundar pichai google" 40
# python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 3 0.7 "megan repinoe redding" 2

# uncomment to produce transcripts

#echo "test 1"
#python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 2 0.7 "bill gates microsoft" 10 > bill_gates_microsoft.txt
#echo "test 2"
# python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 1 0.7 "mark zuckerberg harvard" 10 > mark_zuckerberg_harvard.txt
#echo "test 3"
# python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 2 0.7 "sundar pichai google" 40 > sundar_pichai_google.txt
#echo "test 4"
#  python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 3 0.7 "megan repinoe redding" 2 > megan_repinoe_redding.txt

# format of program, and tests
#  python3 google-query.py <google API Key> <google engine id> <r> <t> <"seed query"> <k>

# r ==> 1 for Schools_Attended, 2 for Work_For, 3 for Live_In, 4 Top_Member_Employees
# t ==> real number between 0 and 1, "extraction confidence threshold"
# seed query ==> e.g. "bill gates microsoft"
# k ==> number of tuples we request in the output
