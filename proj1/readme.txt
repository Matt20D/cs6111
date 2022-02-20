--------------------------------------------------
Proj 1: Readme 
Matthew Duran (md3420)
Ethan Garry (epg2136)
--------------------------------------------------
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
    ├── references.txt
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
to run

2) either uncomment a test case in test.sh, and type `./test.sh` or use the command line
`python3 google-query.py <google api key> <google engine id> <precision> <query>`
example: python3 google-query.py AIzaSyANgIgrPnITWd3HBYXVJpV_WM3mVQd8pME 7c642eecbff553d82 1 "brin"

3) run as many tests as you would like, either using the `./test.sh` file or your own scripts

4) to exit the venv type `deactivate` into the shell.


    ------------------------------------
    Overall Code Description
    ------------------------------------
3) clear description of the code, explaining the general structure of the code
    3) explain how we handle non-html files

    ------------------------------------
    Query Augmentation Algorithm
    ------------------------------------
4) detailed description of query modification method [all important details]
    4) how to pick new words
    4) how the words will be ordered
