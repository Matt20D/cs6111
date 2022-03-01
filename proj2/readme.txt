------------------------------------------------------------
Proj 1: Readme 
Matthew Duran (md3420)
Ethan Garry (epg2136)
------------------------------------------------------------
------------------------------------------------------------
credentials for Google Programmable Search Engine:        
search_engine_id=7c642eecbff553d82                        
JSON_API_KEY=AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME      
project=cs6111                                            
------------------------------------------------------------

    --------------------------------------
    Directory Structure of proj1
    --------------------------------------

├── proj1/
    ├── readme.txt <-- You are reading this file 
    ├── references.txt
    ├── stopwords.txt
    ├── setup.sh [Note: ensure that the shell file has executable permissions]   
    ├── requirements.txt
    ├── test.sh  [Note: ensure that the shell file has executable permissions] 
    ├── google-query.py
    ├── Tokenizer.py
    ├── query_transcripts/ [Note: will be submitted separately as well]
        ├── brin.txt
        ├── cases.txt
        ├── per_se.txt

    ------------------------------------
    How to install and run our software
    ------------------------------------

1) type `source setup.sh` into the command line to run the shell
script which will install all of our dependent packages into a python
venv so that you have all of the packages necessesary for our software 
to run. Please ensure that you have pip3 package manager installed.

2) either uncomment a test case in test.sh, and type `./test.sh` or use the command line
`python3 google-query.py <google api key> <google engine id> <precision> <query>`
example: python3 google-query.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 1 "brin"

3) run as many tests as you would like, either using the `./test.sh` file or your own scripts

4) to exit the venv type `deactivate` into the shell.


    ------------------------------------
    Overall Code Description
    ------------------------------------

google-query.py :: main():

First we parse all of the command line arguments to ensure that
they are all there and properly inputted. Then we will enter an infinite loop which 
will be executed until we beat the precision@k, precision@k = 0, there are not 10 docs
in the first run, of we do beat precision@k.

if we are on the first search, we print the parameters to the console to match the sample
executable and then use the api to query google and get the results. If there are less than
10 results on the first iteration then we will quit the program, since the query was not 
ambiguous at all. Otherwise, every other search we will not check if there are at least 10 
results. However in both cases we will handle non-html files the same, by ignoring them. 
They will not be used in the analysis.

remove_bad_results() will actually remove any documets marked as non-html so we can skip 
them in the analysis.

Then we will present the results to the user and ask for relevance feedback. If the 
returned precition@k is 0, we will quit. If it beats our target, then we are done and will
quit. Otherwise we will try to augment the query using the algorithm (described below) in
order to give google a more well defined query list to hopefully boost our relevance.

In practice we have gotten good query augmentations, and have seen very vague queries pull 
back the documents that we have desired. There are other cases, such as when using wikipedia
that we would get some weird query results passed back. But those have been rare and few and 
far between. Overall we are thrilled with how the program has come out, and how we were able 
to tackle this very complicated and real-world topic.

Tokenizer.py:

This class handles all of the document parsing for us. Its constructor will take in a url so 
that when we ask to get_words() a get request will be executed and then the documents will be 
parsed.

When executing a get request there are chances that we could have exceptions thrown, with 
which we will pass along to the google-query file and make them handle it. Essentially if the 
get request fails then the main program will use the title and snippet on backup in order to 
tokenize and treat that data as the full document.

When the get request doesnt fail we use a beautiful soup web parser to extract the human 
readable text. With which we will use regex matching to pull back words without punctuation, 
and will skip numeric words as well. Furthermore, if the words are stopwords they will also 
be skipped and not returned to the user.

all of the stop words will be read in from prof gravano's stopword file (saved locally) and 
placed into a set which is available within every Tokenizer object.

    ------------------------------------
    Query Augmentation Algorithm
    ------------------------------------

google-query.py :: run_augmentation():

This is the bulk of the assignment where we do all of our analysis of the relevant and 
non-relevant documents in order to return a better query to google for the next iteration.

First we will get the term frequency for each of the documents in RELEVANT_DOCS and 
NON_RELEVANT_DOCS. These documents have been labeled by the user and separated by us for ease 
of manipulation. get_term_frequency() will go through all of the labeled documents and 
instantiate a Tokenizer object. We will first try to get the actual html document via the 
web, but if that fails we will just used the title/snippet that is stored. This method will 
then create a dictionary that is an inverted list containing the term and the documents that 
they belong to.

Once we have the inverted list we will take that structure and convert it to a data frame, I 
will not go into the details because that is just data structure manipulation. But by using 
a DataFrame, we can visualize document column vectors in a much easier to work with format.

Then we will get the log term frequency and the tf_idf weights for both the relevant and non 
relevant documents by just simply applying the formulas from lecture. It was key to have 
copies of all of these data structures becuase there are certain edge cases where we would 
need them.

Next if there were a query of length one or there was only one relevant document we would use 
the tf weights for choosing words. This is because with one column tf idf weights would be 
constant and would not give us any actionable information to use.

Whethere we are in the first or second case we will need to execute the following 3 functions.

In score_rel_docs() we will take in the previous query list along with the dataframe of 
all relevant documents. They are still in preserved order from google's return, which is 
important to the next heuristic. we will essentially take the union of the words in the query
along with the word weight in document column vectors, and take a sum of all the weights. 
This allows us to see how similar the query was to the weights of those words within the 
document. Within this score() mehto we will also apply a word_zone heuristic which will 
give the word weight an extra boost if it hits in the title or the snippet. We consider the 
snippet to be important, because it is the beginning of the html document, so probably the  
most relevant. Lastly, we will return the list of the documents and their score to the caller.

In apply_google_heuristic() we use the document scores from above and will weight them by 
their column label. Recall that we stored the documents in ranked order from google's search 
return, so we wanted to be able to apply a heuristic that uses their results as a proxy for
search importantce. Thus we use a sliding scale, to weight the document sums accordingly. We
have seen some of the final document orderings change as a result of this heuristic.

In choose_words() we now use all of the relevant documents (after their scoring using our
varied heuristics) to pick the best words. We didnt want to limit the way we chose words, 
since the user could have labeled a variety of documents as relevant. Thus we will iterate
throguh all of the relevant documents and choose all of the nonzero words, that have their 
heuristic adjusted weights, and send the value to a max heap. If the word is a stopword, or 
has a stemmed version in the query we will also skip it. Once we go thru all of the relevant  
documents we safely choose the top words from the max heap. We chose 250 words, (yes a lot), 
becasue we wanted a large sample of words and queries to choose from. 

Now that the hard part has been done, we need queries to score and choose from, so we generate
all combinations of the word additions to the previous query list. Thus in the word set from 
above, we will add one word, and then add combinations of adding one additional word from the 
set. This generates a gigantic list of potential queries to score, which we deem a feature 
not a bug.

Again without diving too deeply into the math, there are cases where we use the tf_weights
and cases where we use the tf-idf_weights vectors. Whichever ones we choose to use we need
to pass them to normalize_vectors() which just applies the function from class.

Now that we have all of these potential queries, a very large list, we need to score them to 
choose the best one. In cosine_similarity(), we implement a pseudo Rochhio algorithm 
which incorporates data from both relevant and non relevant documents to score the potential queries. 
We mean pseudo because the algorithm will not return a new query like Rocchio would, but would rather 
score the query list using cosine similarity between the query and the relevant documents 
and the non relevant documents. The goal being that the query be the most similar to the 
relevant docs and the most dissimilar to the non-rel docs. For a while we never considered all of the 
information, and we received poor query results. So by using all of the labeled data we were able to get 
much better results for our final query.

=======================================================================================
Now that we have generated the best possible query we move on to n-grams for ordering.
=======================================================================================

At this stage we have chosen our word(s) for the new query and need to determine the proper ordering.
Although neither of us have a background in NLP, professor Gravano was kind enough to link a research
paper (https://web.stanford.edu/~jurafsky/slp3/3.pdf) on using n_grams to determine the "proper" order
of a query. I put proper in quotations because we ultimately end up using an approximation of the probabilities 
we really want. 

Let's say we have a query "word1 word2 word3 word4". We want to calculate the probability this query occurs in any of
our documents (relevant and non-relevant). In an ideal world, we can calculate the following:

p("word2" given "word1") * p("word3" given "word1 word2") * ...

We would then calculate this probability for every permutation of our query phrase to determine the best order (one with 
the highest probability). These calculations become costly, fast. So, instead, we use an approximation of these probabilities, 
only considering pairs of words at a time. So our new calculation looks something like this:

p("word2" given "word1") * p("word3" given "word2") * ...

This way, we can also store probabilities in a dictionary object and re-use work. This approximation
significantly speeds up our calculations and allows us to make a very well educated guess at the "proper"
order.

We had to develop 2 additional global data structures to implement this algorithm: WORD_COUNT and N_GRAM_MASTER_LIST.
WORD_COUNT is simply a frequency for ALL terms throughout given documents (including stop words). N_GRAM_MASTER_LIST 
contains all the terms from our returned documents IN ORDER. We use this list to determine p("word2" given "word1") etc.

We ran into some issues with larger undirected queries. If the user deviated from the original purpose and allowed the
query to expand over 10 terms, calc_n_grams starts to hang. The permuations become too great to be calculated in a 
reasonable amount of time. Based on the advice from Ed we've determined this scenario is out of scope as the user will 
not be deviating from their original goal. If we did have to consider this scenario, we would implement a random sampling
of all the queries or impose a time limit on the function.