# PDF2Text

Given a `data.csv` file, whose first column has urls to pdf files, `pdf2text.py` will download the pdfs, and extract the text from them.

## Pre-requisites

- The code will work with python>=3.7
- Create a virtual environment , either using `conda` or `venv`
- To create a virtual environment using anaconda, do the following:
    - `conda create -n pdf2text`
    - `conda activate pdf2text`
- Ensure `pip` is installed within the `conda` environment, by running `which pip`
    - If `pip` isn't pointing to a location within the conda environment just created, run `conda install pip` 
      inside the environment to install `pip`
- `pip install -r requirements.txt`

## Usage
`python pdf2text.py`
- Assumes that a `data.csv` file is present in the current directory.
    - To change the filename, change the `INPUT_FILE_PATH` variable in `config.py`

## Implementation Details:
1. Uses multiprocessing.
2. Can extract images from both direct (.pdf) and indirect urls (webpages containing pdf links)
3. output format:
    ```
    [
        {
            "page-url":"https://some/url/",
            "pdf-url":"https://1.pdf",
            "pdf-content":"output/1.txt"
        },
        {
            "page-url":"https://some/url2/",
            "pdf-url":"https://2.pdf",
            "pdf-content":"output/2.txt"
        },
        .,
        .,
        {
            "page-url":"https://some/urln/",
            "pdf-url":"https://n.pdf",
            "pdf-content":"output/n.txt"
        }
    ]
    ```
