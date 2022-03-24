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
    ├── dir_cleanup.sh*
    ├── setup.sh* [Note: ensure that the shell file has executable permissions]   
    ├── my_requirements.txt
    ├── test.sh*  [Note: ensure that the shell file has executable permissions] 
    ├── getSpacy.sh* [Note: ensure that the shell file has executable permissions] 
    ├── getSpanBert.sh* [Note: ensure that the shell file has executable permissions] 
    ├── iterative-set-expansion.py
    ├── Tokenizer.py
    ├── .gitignore
    ├── transcripts/ [Note: will be submitted separately as well]
        ├── bill_gates_microsoft.txt [TODO] 
        ├── megan_repinoe_redding.txt [TODO] 
        ├── mark_zuckerberg_harvard.txt [TODO] 
        ├── sundar_pichai_google.txt [TODO] 

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


TODO 

A transcript of the run of your program on input parameters: 2 0.7 "bill gates microsoft" 10 (i.e., for r=2, t=0.7, q=[bill gates microsoft], and k=10). The format of your transcript should closely follow the format of the reference implementation, and should print the same information (i.e., number of characters, sentences, relations, etc.) as the corresponding session of the reference implementation.
