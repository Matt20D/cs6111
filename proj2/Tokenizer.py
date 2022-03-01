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

        # making the soup object
        # request.text is the markup; this ensures we only receive back the human
        # readable part of the web page, no meta data
        # using the html parser
        soup = bs(request.text,"html.parser")   
    
        print(soup)
        quit()
        return None
    

          
                         
 