------------------------------------------------------------
Proj 2: Readme 
Matthew Duran (md3420)
Ethan Garry (epg2136)
------------------------------------------------------------
------------------------------------------------------------
credentials for Google Programmable Search Engine:        
search_engine_id=<client-key>                        
JSON_API_KEY=<api-key>     
project=cs6111                                            
------------------------------------------------------------

    --------------------------------------
    Directory Structure of proj2
    --------------------------------------

├── proj2/
    ├── readme.txt <-- You are reading this file 
    ├── sources.txt
    ├── dir_cleanup.sh* [Note: ensure that the shell file has executable permissions]   
    ├── setup.sh* [Note: ensure that the shell file has executable permissions]   
    ├── my_requirements.txt
    ├── test.sh*  [Note: ensure that the shell file has executable permissions] 
    ├── getSpacy.sh* [Note: ensure that the shell file has executable permissions] 
    ├── getSpanBert.sh* [Note: ensure that the shell file has executable permissions] 
    ├── iterative-set-expansion.py
    ├── Tokenizer.py
    ├── .gitignore
    ├── transcripts/ [Note: will be submitted separately as well]
        ├── bill_gates_microsoft.txt 
        ├── megan_repinoe_redding.txt  
        ├── mark_zuckerberg_harvard.txt  
        ├── sundar_pichai_google.txt 

    ------------------------------------
    How to install and run our software
    ------------------------------------

NOTE: the shell script files that we wrote need to have executable
permissions, you can use `chmod 700` to give rwx to the .sh files

1) type `source setup.sh` into the command line to run the shell
script which will install all of our dependent packages into a python
venv so that you have all of the packages necessesary for our software 
to run. Please ensure that you have pip3 package manager installed. Further,
setup.sh will also call the getSpacy.sh and getSpanBert.sh files that will 
install the dependencies and move all of the spanBERT files from that cloned
directory up a level to where my source code is.

  NOTE: Our Source code depends on the fact that all of the spanbert files
  from the cloned repo are located at the same level as the source code. So
  in the even the shell script fails, ensure that you clone the repo and
  move all of the spanbert ML files to the same directory where
  iterative-set-expansion.py and Tokenizer.py are located.

2) either uncomment a test case in test.sh, and type `./test.sh` or use the command line
`python3 iterative-set-expansion.py <google api key> <google engine id> <r> <t> <q> <k>`
example: python3 iterative-set-expansion.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 3 .8 "megan repinoe redding" 10

  2.1) run as many tests as you would like, either using the `./test.sh` file or your own scripts

3) to clean the directory run `dir_cleanup.sh` and it will remove all of the
relocated spanbert files.

4) to exit the venv type `deactivate` into the shell.

In the event that any of the software package installations fail, you can manually do the
following steps:

create virtual environment for our software dependencies:
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r my_requirements.txt

determine the issue with spanbert:
    clone the repo, and move all of the files up a dir to where my source
    code is.

Sometimes there are issues with installing bert, so you may need to 
troubleshoot that, but our code needs the dependencies in my_requirements.txt 
to be able to run!

    ------------------------------------
    Overall Code Description
    ------------------------------------

There are two main files in this software pacakge iterative-set-expansion.py
and Tokenizer.py. I will talk about Tokenizer.py in the ISE algorithm
section.

------------------------------------
iterative-set-expansion.py:
------------------------------------

Beginning at the main method we will do standard parameter checks to ensure
that they meet the constraints necessary for the program to run. Then I will
create an all_queries set, which will track all of the tuples that have been
used for interfacing with google except the seed query. There is no
systematic way to break the seed query into subj and obj, so we just track
the seed query separately. Next, we make sets for the URLs that have been
seen (to ensure we don't double dip in a document) and a dictionary which
will contain the extracted tuples. We chose a dictionary as the DS becasue
this allows us to update the confidence (used as value) of a tuple (used 
as a key) in a much simpler way.

Then the main loop will run as long as we have not hit the desired k-tuple
benchmark. For a given iteration we will print all of the parameters
(query,confidence threshold, etc). and then use google api with a seed
query. Then for the resultant list of "hopefully" 10 urls we will go through
them one by one. If we have seen the url, simply skip it, otherwise we will
need to process it. We will then pass the url, the set of X tuples, the
desired relation, and confidence threshold to do_pipeline(). I will cover
that later. do_pipeline() will pass the dictionary as a memory address so
the returned dict has already been updated with new tuples extracted (if
any).

Then if we have to determine if we need to set a new seed query. If we have
seen k-tuples break out of the main loop and proceed to printing all of the
relations. Else, we sort all of the tuples by confidence in decreasing order
and choose the next not queried relation and use it as a new seed. In this
process if we go through all of the tuples, then we have stalled and break
the loop, log the event, and print the results. Otherwise, we need to see 
if the tuple has been used in querying and/or is somehow the seed query. If 
that is not the case we can update the seed and proceed to the next iteration.

Once the loop is broken, either by a stall, or by the fact that we have
found at least k tuples we need to print them! Sort them in decreasing order
of confidence, and print out the tuples.

In do_pipeline() we will instantiate a Tokenizer object, which will execute
all of the get request and do all of the text parsing and manipulation. We
execute the get request and then will extract the tuples from the object and
return it to the caller. This is the function that handles the actual data
pipeline. IT will also handle http errors (timeouts, and the like). Where if
something fails, we will just return the set of tuples that were passed in
to the function like nothing happened.

    ------------------------------------
    Relation Extraction Algorithm
    ------------------------------------

------------------------------------
Tokenizer.py
------------------------------------

check_sentence_entities(): This function will take a sentence that has all
of the spacy extracted entities and tell the caller that this sentence
should be further processed. If we do not have entities that can satisfy a
valid relation then this sentence can be skipped. Thus, I am checking to see
that at a minimum we can make ONE pair of a valid (subj, obj) that will
satisfy the relation. There may be way more than one pair, but we need one
in order to continue to use bert. This is a mechanism to prune the search
space and only use bert when we can actually extract some pertinent
information.

is_valid_relation(): given a pair I will determine that the subject and
object satisfy a valid relation. This takes place after all the pairs have
been made. sometimes we may have the valid relation in reverse order, so we
want to exclude that from bert. If the pair is valid then we can use it for
bert safely. Otherwise, we will not add this to the candidates. This
is_valid_relation() is used to prune the full list of pairs, to all of the
relevant candidate_pairs for bert. This method will reduce the space
considerably.

Tokenizer constructor will store all of the relevant class variables so that
I can use them later on.

execute_get_request(): here we try to get the webpage link data. If there is
an error, then we raise an exception that is handled by the caller. On
success we will then use beautiful soup to parse the data. If the extracted
sentence is more than 2000 chars we will truncate (for efficiency),
otherwise nothing is needed to be done.

Next we will use spacy to extract sentences from the document that we will
need to iterate through. Some of these commands are largely similar to those
in the provided shell scripts (that we were instructed to use).

For each sentence we will use the spacy get_entities() method that will tell
us all of the entities that can possibly extracted by this sentence. We then
need to call check_sentence_entities() to determine if we can make a valid pair
from a the sentence. This allows us to determine if this sentence is going
to be a waste of time. If we cannot, then skip the sentence, else lets move
forward with processing.

Next we will create_entity_pairs() using the spacy method, which we will then
pass to is_valid_relation() tells us if the pair is valid. the spacy method
will produce all permutations of the entities, most of which are invalid. my
is_valid() method will significantly prune that space, and print out how
many candidates are left for bert to work with.

If there are no candidates left, then we spared bert a waste of time so
continue on to next sentence in the doc. Otherwise we will call the spanbert
predict method on all of the candidates. We then will need to iterate
through all of the predictions that bert made.

For each of the predictions, we first need to ensure that the extracted
predicted relation matches the one that we are searching for (see special 
note section below, because this is a point of contention). 
If the tuple is indeed what we are looking for then we will print all of 
the data associated with it, and do some further checks. If the tuple has 
a confidence higher then threshold we continue processing, otherwise
discard. We then need to check to see if the tuple is already in the map. 
If it is not, then we found a new one, add it. Otherwise we need to see if the new
confidence is higher than the one on record. If it is, then update it,
otherwise do nothing. We have seen cases where we extract the same tuple a
lot of times, but if the confidence is not as high as the one on record no
updates need to be made. We will then lastly, print out the total number
of tuples that have been extracted out of this document for the console log.


    ------------------------------------
    Important Note regarding SPANBERT Filtering
    ------------------------------------

We believe that the number of iterations that the code takes to complete is
highly correlated with the output relation that spanbert model produces. We 
have documented cases on Edstem where spanbert receives subj: "megan
Rapinoe" and obj: "redding" for the Live_In relation and we can receive two
different outputs. I have extracted the same pair and passed to bert
back-to-back and have received a "no_relation" followed by the correct 
"per:cities_of_residence" predicted relation. Thus, before we chose to filter
out all of those tuples that don't match the desired relation we were
extracting hundreds of tuples (all valid by subject and object, but maybe
spanbert extracted "no_relation"), and now we mostly hit the target like 
in the reference implementation.

Keep in mind that we are passing only pairs that have the CORRECT subject
entity pairs into spanbert, so we believe the potential noise in the tuple
extraction/iteration number comes from the spanbert model which we cannot
control. Thus, hopefully doesn't hurt the overall grade, in the case we were
not hitting the required iteration benchmark.
