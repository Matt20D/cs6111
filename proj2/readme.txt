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

Sometimes there are issues with installing bert, so you may need to trouble
shoot that, but our code needs the dependencies in my_requirements.txt to be
able to run!

    ------------------------------------
    Overall Code Description
    ------------------------------------

  talk about all the external libraries here too

    ------------------------------------
    Relation Extraction Algorithm
    ------------------------------------

A detailed description of how you carried out Step 3 in the "Description" section above

    ------------------------------------
    Important Note regarding SPANBERT Filtering
    ------------------------------------

We believe that the number of iterations that the code takes to complete is
highly correlated with the output relation that spanbert model produces. We 
have documented cases on Edstem where spanbert receives subj: "megan
Rapinoe" and obj: "redding" for the Live_In relation and we can receive two
different outputs. I have extracted the same pair and passed to bert back to
back and have received a "no_relation" followed by the correct 
"per:cities_of_residence" predicted relation. Thus, before we chose to filter
out all of those tuples that don't match the desired relation we were
extracting hundreds of tuples, and now we mostly hit the target like in the
reference implementation.

Keep in mind that we are passing only pairs that have the CORRECT subject
entity pairs into spanbert, so we believe the potential noise in the tuple
extraction/iteration number comes from the spanbert model which we cannot
control.
