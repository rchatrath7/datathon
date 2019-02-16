import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import threading 

def scrape(query, startdate, enddate):
    """
        Scrapes webpage given root and returns array of web elements
        
        Parameters
        ----------
        query       : search query as string
        startdate   : date of first tweet as <year>-<month>-<day> ex: 2018-06-01
        enddate     : date of last tweet as <year>-<month>-<day>
        
        Returns
        -------
        Tweets as web elemtns
        """
    browser = webdriver.Chrome()
    base_url = u'https://twitter.com/search?l=&q='
    sub_url = u"{} %20since%3A{} %20until%3A{}&src=typd&lang=en".format(query, startdate, enddate) 
    url = base_url+sub_url
    
    browser.get(url)
    time.sleep(1)
    body = browser.find_element_by_tag_name('body')
    
    for _ in range(5000):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
    
    tweets = browser.find_elements_by_class_name('tweet-text')
    

    return tweets

def readTextFile(filePath):
    """
        reads in and returns text file as list of strings
        
        Parameters
        ----------
        filePath    : directory path
        
        Returns
        -------
        List of strings
        """
    text_file = open(filepath, "r")
    list = text_file.readlines()
    return list

def saveTweets(tweets, fileName):
    """
        saves scrapped tweets to .txt file
        
        Parameters
        ----------
        tweets      : list of web elements from scrape
        fileName    : name file will be written to as a string
        
        """
    output = fileName+".txt"
    with open(output, 'w') as f:
        for tweet in tweets:
            f.write(str(tweets.text) +"\n")

def proto_exec(tweet_args, filepath): 
    twitter = scrape(*tweet_args) 
    saveTweets(twitter, filepath) 

start_year = 2009 
end_year = 2010 

threads = [threading.Thread(target=proto_exec, 
            args=(("Honeywell", "{}-01-01".format(start_year + i), "{}-12-31".format(start_year + i)), "output_{}".format(start_year + i),))
            for i in range(end_year-start_year+1)
          ]

for thread in threads: 
    thread.start() 

for thread in threads: 
    thread.join() 

## example for honeywell from 6/1/2018 to 12/31/18
# twitter = scrape("Honeywell", "2009-01-01", "2009-12-31")
# saveTweets(twitter, "output")
