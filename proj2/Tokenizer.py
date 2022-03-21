"""
file: Tokenizer.py
description: Tokenizer class used for parsing html documents into tokens
which is a big part of the document analysis. We need to be able to 
get a list of all the words in a document so that we can create inverted
lists.
authors: Matthew Duran and Ethan Garry
"""

#
# Library Modules Needed
#

import requests # use to execute a get request
from bs4 import BeautifulSoup as bs # scraper
import re # regex
import spacy
from SpanBERT.spacy_help_functions import * #import spacy help
from SpanBERT.spanbert import SpanBERT 

spanbert = SpanBERT("./SpanBERT/pretrained_spanbert")  

class Tokenizer(object):

    def __init__(self, url):
        self.webpage       = url
    
    def execute_get_request(self) -> None:
        
        # send get request for the webpage
        try:
        
            request = requests.get(self.webpage)
        except:
            # raise exception, so that we just use the stored title and snippet
            raise requests.exceptions.HTTPError

        # if the request status is not "200" ok then throw an exception
        # the code will then simply used the stored snippet and title
        if request.status_code != 200:
            raise requests.exceptions.HTTPError


        
        # Extract text
        # source: https://www.geeksforgeeks.org/remove-all-style-scripts-and-html-tags-using-beautifulsoup/
        soup = bs(request.text, "html.parser")
 
        for data in soup(['style', 'script']):
        # Remove tags
            data.decompose()

        soup_text = ' '.join(soup.stripped_strings)        
     
        # get first 20k characters as specified in assignment prompt
        soup_text = soup_text if len(soup_text)<=20000 else soup_text[:20000]

        nlp = spacy.load("en_core_web_lg")
        doc = nlp(soup_text)
        entities_of_interest = ["ORGANIZATION", "PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]
        print('working on new doc')
        relations = extract_relations(doc, spanbert, entities_of_interest)
        if len(relations.keys())>0:
            print("Relations: {}".format(dict(relations)))


        return relations
    

          
                         
 