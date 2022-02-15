import requests # use to execute a get request
from bs4 import BeautifulSoup as bs # scraper
import re # regex

class Tokenizer(object):

    def __init__(self, url):
        self.webpage       = url
        self.parsed_words  = []
        self.STOPWORDS_SET = self.get_stopwords()
    
    #
    # Use these methods to do stop word elimination
    #

    # get list of stopwords from gravano's file saved locally
    def get_stopwords(self) -> set():

        # open the file to parse the stopwords and build a set
        try:
            stopwords = set()
            with open("stopwords.txt", "r") as infile:
                for word in infile:
                    clean_word = word.strip()
                    stopwords.add(clean_word)	
            infile.close()
            return stopwords
        
        # error with parsing the file, so we cannot do stopword elimination
        except:
            return set()

    # use for stopword elimination
    def is_stopword(self, word: str) -> bool:
        return word in self.STOPWORDS_SET

    #
    # Use these methods for parsing file for keywords and cleaning them up
    #

    # defined this separately, so that if the get request fails, we can just use
    # the data that we have previously stored
    # success determines whether the request was successful or not
    def regex_match(self, string, success: bool) -> list:
        
        # match any alphanumeric char one or more times (i.e a word), remove all punctuation.
        regex = "\w+"

        # regex match and pull back all of the valid string, regex defined above
        keywords = re.findall(regex, string)
        
        # we only compare lowercase versions of word
        if success:
            keywords = [word.lower() for word in keywords if not (self.is_stopword(word) or word.isnumeric())]        
            return keywords
        else:
            # we got here by an exception and are just storing snippet and title
            res = []
            for i in range(len(keywords)):
                word = keywords[i]
                if not (self.is_stopword(word) or word.isnumeric()):
                    res.append([word.lower(), i+1])
            return res

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
 
        docstrings = soup.stripped_strings
        
        # keep track of word position in document with i
        i = 1 
        for string in docstrings:
                        
            # we only compare lowercase versions of word
            keywords = self.regex_match(string, True)

            # append to master list

            for word in keywords:
                
                # perform stopword elimination
                # also if the word is actually a number, get rid of it
                if self.is_stopword(word) or word.isnumeric():
                    #print("{} is a stopword".format(word))
                    continue

                # this word is not a stopword, save it
                self.parsed_words.append([word, i])
                i += 1
        
        
        

    # use this accessor method to get list of words from html file
    def get_words(self) -> list:

        self.execute_get_request()
        
        return self.parsed_words