# WikiExtractor

Given a keyword, `wiki_extractor.py` will extract urls containing information related to the keyword and one paragraph from the corresponding wikipedia page.

## Pre-requisites

- The code will work with python>=3.7
- Create a virtual environment , either using `conda` or `venv`
- To create a virtual environment using anaconda, do the following:
    - `conda create -n wikiExtractor`
    - `conda activate wikiExtractor`
- Ensure `pip` is installed within the `conda` environment, by running `which pip`
    - If `pip` isn't pointing to a location within the conda environment just created, run `conda install pip` 
      inside the environment to install `pip`
- `pip install -r requirements.txt`

## Usage
`python wiki_extractor.py --keyword (or -k) <key_word_string> --num_urls (or -n) <num_urls_to_retrieve> --output (or -o)  <filename>.json`

**Example**
- `python wiki_extractor.py --keyword "Hello World" --num_urls 10 --output output.json`
- or alternatively , `python wiki_extractor.py -k  "Hello World" -n 10 -o output.json`

### Flags:

- `--keyword` or `-k` flag is a required arguement and there is no default value set. 
    - If keyword has multiple words, pass it within quotes as shown above.

- `--num_urls` or `-n` flag is set to retrieve atmost `--num_urls` number of wikipedia pages.
    - atmost because there could be keywords with lesser number of search results.
    - default : set to 10

- `--output` or `-o` flag : send in a file name with `.json` extention.
    - default: `output.json`
    - If you are looking to use this program to extract data for multiple keywords, ensure you give different filenames inorder to avoid overwriting.


## Output

- Output will be created in the current folder with the file name provided at input using the `(-o or --output)` flags. If no input is provided, the default file name is `output.json`

### Output Format:
- the json file will be of the following format:
```
    [
        {
            "url":https:/url/to/page_1/,
            "paragraph":<first paragraph in the above url>
        },
        {
            "url":https:/url/to/page_2/,
            "paragraph":<first paragraph in the above url>
        },
        .,
        .,
        {
            "url":https:/url/to/page_n/,
            "paragraph":<first paragraph in the above url>
        }
    ]
```


