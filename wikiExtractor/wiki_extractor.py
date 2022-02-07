"""
author: @bvkhadiravana

# Points to Note:
1. Code uses multi-processing -- and to do so uses 80% of your CPU.
2. Read Readme.md for usage.
3. The upper limit for a query set by Wikipedia is 500, have used offsets in query to process
   requirements of more than that.

"""
import argparse
import requests
from bs4 import BeautifulSoup
import json
import time
import multiprocessing 
from multiprocessing import Pool

# global constants defined in constants.py
from constants import API_URL,API_MAX_PAGE_LIMIT,MIN_NUMBER_OF_CPUS , PERCENTAGE_CPUS

NUMBER_OF_CPUS = max(MIN_NUMBER_OF_CPUS,int(multiprocessing.cpu_count()*PERCENTAGE_CPUS)) # using PERCENTAGE_CPUS% of cpus



def getFirstPara(wikiURL:str):

    """
        Function receives first para
        Input:
            wikiURL : string, 
                      valid wikipage url

        Called By: extractWikiData

        Note:
            The code also retrieves exactly one paragraph. most times, this paragraph will correspond
            to the first paragraph that any user sees on clicking the corresponding link. However, 
            I have found very very few cases where the paragraph in the HTML response is not exactly the 
            first para that we see on the wikipedia page.

            If the first summary is needed (which can include multiple paras), the implementation can be easily 
            changed to calling wikipedia.summary() function from the wikipedia api.
    """

    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.get(wikiURL,headers = headers)
        data = response.text
        htmlParse = BeautifulSoup(data, 'html.parser')
    except:
        print(f"Error in extracting paragraph from {wikiURL}")
        return None

    try:
        allPs = htmlParse.find_all("p")
        print(f"Successfully retrieved first para of {wikiURL}")
        if len(allPs[0].text) > 1:
            para = allPs[0].text
        else:
            para = allPs[1].text # first paragraph (index:0) seems to be empty in most wikipedia pages
        return para 

    except:
        # take care of wikipedia pages with no paragraph (for example only tables)
        return ""
    
def titleToURL(wikiTitles:list):

    """
        Observations:
            Function converts wikipadia titles to urls
            From observation, wikipedia urls are just https://en.wikipedia.org/wiki/ followed by title 
            having their spaces replaced with "_"

            i.e. a wiki page with the title "Computer science" (without the quotes), has the url 
            https://en.wikipedia.org/wiki/Computer_science

        Input:
            wikiTitles : list, 
                         list of valid wikipedia titles
                      
        Called By: extractWikiData
    """

    urls = []
    for title in wikiTitles:
        urls.append("https://en.wikipedia.org/wiki/"+"_".join(title.split(" ")))
    
    return urls

def extractWikiData(keyword:str,num_urls:int,outfile:str):
    """
        Input:
            keyword:
                dtype: str
                semantics: keyword string to be searched through the wikimedia api.
                example: "IIIT Hyderabad"
            num_urls:
                dtype: int
                semantics: number of results to be searched.
                default: 10 (same as the default set by the wikimedia api)

            outfile:
                dtype: str
                semantics: File name of the output file.
        Output:
            Return: Null
            Effect: Creates a file named `output.json` 

        
    """
    
    sess = requests.Session()


    pageTitles = []
    errorFlag = False
    while True:

        srlimit = min(API_MAX_PAGE_LIMIT,num_urls-len(pageTitles))
        offset = len(pageTitles)
        # print(f"srlimit : {srlimit}, offset : {offset}")
        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": keyword,
            "sroffset":offset,
            "srlimit": srlimit,
        }

        try:
            response = sess.get(url=API_URL, params=PARAMS)
        except Exception as e:
            errorFlag = True
            print(f"An error occured while trying to search for the page with keyword {keyword}")
            print("Terminating ...")
            print(e)
            break
        
        res = response.json()
        search_results = [d['title'] for d in res['query']['search']]

        pageTitles+=search_results

        print(f"Extracted {len(pageTitles)}/{num_urls} wikipedia pages.")

        if len(pageTitles)==num_urls or len(search_results)!=srlimit:
            print(f"Queried for {num_urls} pages, received only {len(pageTitles)} results from the api.")
            break
    
    if not errorFlag and len(pageTitles) > 0:
        jsonData = []
        urls = titleToURL(pageTitles)

        
        print(f"*** Retrieving Text using {NUMBER_OF_CPUS} cpus ***")

        # retrieving one para using the urls and multiple cpus.
        with Pool(NUMBER_OF_CPUS) as p:
            results = p.map(getFirstPara, urls)
        
        for i,result in enumerate(results):
            if result is not None:
                jsonData.append(
                    {
                        "url":urls[i],
                        "paragraph":result
                    }
                )
        print(f"Writing {len(jsonData)} data points to ./{outfile}")
        with open(outfile,'w') as f:
            json.dump(jsonData, f,indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-kw",
                        "--keyword",
                        help="Important keywords required to retrieve information from wikipedia",
                        type=str,
                        required=True
                       )
    parser.add_argument("-n",
                        "--num_urls",
                        help="Maximum number of urls to retrieve from wikipedia",
                        type=int,
                        default=10
                       )
    parser.add_argument("-o",
                        "--output",
                        help="output file name",
                        type=str,
                        default="output.json"
                       )
    args = parser.parse_args()
    
    start = time.time()
    extractWikiData(args.keyword, int(args.num_urls), args.output)
    end = time.time()
    print(f"Time taken : {end-start} s")
    