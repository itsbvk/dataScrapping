API_URL = "https://en.wikipedia.org/w/api.php"
API_MAX_PAGE_LIMIT = 500 
# from wikimedia documentation (don't increase number unless number has increased in the wikipedia documentation)
MIN_NUMBER_OF_CPUS = 2 
PERCENTAGE_CPUS = 0.8 # fraction between 0 and 1. Will use this much percent of cpus for multiprocessing