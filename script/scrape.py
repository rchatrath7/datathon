import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import threading 

def scrape(url, text_class_name, date_class_name):
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
    # browser = webdriver.Chrome()
   #  chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--lang=en')
   #  chrome_options.add_argument('CHROME')
    browser = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.CHROME)
    
    browser.get(url)
    body = browser.find_element_by_tag_name('body')

    # for _ in range(100): 
        # body.send_keys(Keys.PAGE_DOWN) 
        # time.sleep(0.2)
    
    while True: 
        try: 
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)
        except KeyboardInterrupt: 
            resp = input("Continue? [y]\\c\\n\n")
            if resp == "y": 
                continue 
            elif resp == "c":
                try: 
                    t = browser.find_elements_by_class_name(text_class_name)[-1] 
                    for _ in range(100): 
                        body.send_keys(Keys.PAGE_DOWN)
                        time.sleep(0.2)
                    b = browser.find_elements_by_class_name(text_class_name)[-1] 
                    print (t, b) 
                    if t == b: 
                        print("Breaking!")  
                        break 
                    else: 
                        print("No break!")
                except Exception: 
                    print("Exception") 
                    break 
            else: 
                break 

    tweets = browser.find_elements_by_class_name(text_class_name)
    dates = browser.find_elements_by_class_name(date_class_name)
    

    return tweets, dates

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

def saveTweets(tweets, dates, fileName):
    """
        saves scrapped tweets to .txt file
        
        Parameters
        ----------
        tweets      : list of web elements from scrape
        dates       : dates of each tweet
        fileName    : name file will be written to as a string
        
        """
    output = fileName+".txt"
    with open(output, 'w') as f:
        for i in range(len(dates)):
            f.write(str(dates[i].text) + " - " + str(tweets[i].text) +"\n")

def construct_url(query, twitter=True, startdate=None, enddate=None): 
    if twitter: 
        base_url = u'https://twitter.com/search?l=&q='
        sub_url = u"{} %20since%3A{} %20until%3A{}&src=typd&lang=en".format(query, startdate, enddate) 
        url = base_url+sub_url
    else: 
        url = u'https://stocktwits.com/symbol/{}'.format(query)

    return url 

def proto_exec(tweet_args, filepath, query, twitter=True, startdate=None, enddate=None): 
    url = construct_url(query, twitter, startdate, enddate) 
    twitter, dates = scrape(url, *tweet_args) 
    saveTweets(twitter, dates, filepath) 

start_year = 2019 
end_year = 2019 

tweet_args = ("tweet-text", "time")
stocktwit_args = ("st_2giLhWN", "st_HsSv26f") 

twitter_args = (
    tweet_args,
    "output_twitter_{}", 
    "Honeywell", 
    True, 
    "{}-01-01", 
    "{}-02-15"
) 

stocktwit_args = (
    stocktwit_args, 
    "stocktwit_output_mmm", 
    "MMM",
    False, 
    None, 
    None 
)

def ex(payload, threaded): 
    if threaded: 
        threads = [threading.Thread(target=proto_exec, 
                    args = (payload[0], payload[1].format(start_year+i), payload[2], payload[3], payload[4].format(start_year+i), payload[5].format(start_year+i),))
                    for i in range(end_year-start_year+1)
                  ]

        for thread in threads: 
            thread.start() 

        for thread in threads: 
            thread.join() 
    else: 
        proto_exec(*payload)

ex(stocktwit_args, False)

## example for honeywell from 6/1/2018 to 12/31/18
# twitter = scrape("Honeywell", "2009-01-01", "2009-12-31")
# saveTweets(twitter, "output")
