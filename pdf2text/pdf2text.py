import sys
import os
import requests
import shutil
import multiprocessing
from multiprocessing import Pool
import csv
from pdf2image import convert_from_path
import cv2
import pytesseract
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json

# from pdf2images import convertPDFs2Imgs,processPDFs

# global constants -- defined in config.py
from config import INPUT_FILE_PATH , PDF_FILES_FOLDERS , MIN_NUMBER_OF_CPUS , PERCENTAGE_CPUS ,VALID_PDF_EXTENTION , OUT_TXT_FILES , CONFIG , OUTFILE

NUMBER_OF_CPUS = max(MIN_NUMBER_OF_CPUS,int(multiprocessing.cpu_count()*PERCENTAGE_CPUS)) # using PERCENTAGE_CPUS% of cpus




def convertPDFs2Imgs(pdfPath):
    """
        pdfPath: str

        Objective: Given a pdf file path, this function creates an image from each page of the pdf file
    """
    print(f"Processing {pdfPath}")
    root = "/".join(pdfPath.split("/")[:-1])

    imgFolder = os.path.join(root,"pdfImgs")
    if os.path.exists(imgFolder):
        shutil.rmtree(imgFolder)
    
    os.mkdir(imgFolder)

    images = convert_from_path(pdfPath)

    for i,img in enumerate(images):
        print(f"Processing {pdfPath} , image {i}")
        img.save(os.path.join(imgFolder,'page_'+ str(i) +'.jpg'), 'JPEG')

def processPDFs(pdfsFolder = PDF_FILES_FOLDERS):
    """
    Parallel pdf 2 image implementation
    """
    localPDFPaths = []
    for root, dirs, files in os.walk(PDF_FILES_FOLDERS):
        for file in files:
            if file[-4:]==VALID_PDF_EXTENTION:
                localPDFPaths.append(os.path.join(root,file))
    
    with Pool(NUMBER_OF_CPUS) as p:
        p.map(convertPDFs2Imgs, localPDFPaths)





def readCSV(path2File):
    """
        returns a list of links to pdfs.
        Assumes the first column of the csv file corresponds to the links

    """

    pdfFileLinks = []
    with open(path2File, newline='') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            pdfFileLinks.append(row[0])
    
    return pdfFileLinks

def downloadPDF(args):
    """
        - Given a .pdf link, this will downlad the file.
    """
    url = args[0]
    idx = args[1]
    os.mkdir(os.path.join(PDF_FILES_FOLDERS,str(idx)))
    fname = os.path.join(PDF_FILES_FOLDERS,str(idx),str(idx)+".pdf")

    with open(fname, 'wb') as f:
        print(f"downloading file with {idx} ...")
        f.write(requests.get(url).content)
        print(f"successfully downloaded file with {idx} ...")
    

def indirectURL2DirectURL(args):
    """
        -- Given a page which contains pdf, this function will download the pdf.
    """
    url = args[0]
    idx = args[1]
    outfolder = os.path.join(PDF_FILES_FOLDERS,str(idx))
    os.mkdir(outfolder)
    fname_pdf = os.path.join(outfolder,str(idx)+".pdf")
    fname_txt = os.path.join(outfolder,str(idx)+".txt")

    print(f"Started downloading file with {idx} ... INDIRECT ....")

    response = requests.get(url)
    soup= BeautifulSoup(response.text, "html.parser")   

    for link in soup.select("a[href$='.pdf']"):
        pdf_url = urljoin(url,link['href'])
        with open(fname_pdf, 'wb') as f:
            f.write(requests.get(pdf_url).content)
        print(f"Downloaded file with {idx} ... INDIRECT ....")
        return pdf_url
    
    
    

def getPDFs(pdfFiles):
    
    directPDFs = []
    pdfsInURL = []
    URLS = [None for i in range(len(pdfFiles))]
    for idx , url in enumerate(pdfFiles):
        if url[-4:]==VALID_PDF_EXTENTION:
            directPDFs.append((url,idx))
            URLS[idx] = url
        else:
            pdfsInURL.append((url,idx))
    
    print("*** DOWNLOADING DIRECT PDFS ***")

    with Pool(NUMBER_OF_CPUS) as p:
        results = p.map(downloadPDF, directPDFs)


    print("*** DOWNLOADING IN-DIRECT PDFS ***")
    with Pool(NUMBER_OF_CPUS) as p:
        indResults = p.map(indirectURL2DirectURL, pdfsInURL)

    for i,x in enumerate(pdfsInURL):
        _,idx = x
        assert URLS[idx] == None
        URLS[idx] = indResults[i]

    return URLS

def ocrOnImage(im_pth):
   
    """
    -- Performs the ocr operation using tesseract api.
    -- Tried with Devanagari and Marathi models. From what I observed no major difference.
    
    """
    print(f"Going to OCR {im_pth}")
    im = cv2.imread(im_pth)
    text = pytesseract.image_to_string(im, config=CONFIG)
        
    print(f"OCRed {im_pth}")
    return text


def extractText():
    """

    Executes Multi-processing on pdfs
    
    """
    if os.path.exists(OUT_TXT_FILES):
        print("Removing")
        shutil.rmtree(OUT_TXT_FILES)
    os.mkdir(OUT_TXT_FILES)

    files = ["42"]
    files = [os.path.join(PDF_FILES_FOLDERS,x) for x in files]

    for filePath in files:
        path2Imgs = os.path.join(filePath,"pdfImgs")

        print(f"Processing {path2Imgs}")
        imgFiles = os.listdir(path2Imgs)
        imgFiles = sorted(imgFiles,key = lambda x: int(x.split("page_")[1].split(".jpg")[0]))
        imgFiles = [os.path.join(path2Imgs,x) for x in imgFiles]
        
        with Pool(NUMBER_OF_CPUS) as p:
            results = p.map(ocrOnImage, imgFiles)

        outFileName = os.path.join(OUT_TXT_FILES,filePath.split("/")[1]+".txt")
        outString = "\n".join(results)
        print(outString)
        with open(outFileName,'w') as f:
            f.write("\n".join(results))


if __name__ == "__main__":
    if os.path.exists(PDF_FILES_FOLDERS):
        print("Removing")
        shutil.rmtree(PDF_FILES_FOLDERS)
    os.mkdir(PDF_FILES_FOLDERS)

    pdfFiles = readCSV(INPUT_FILE_PATH)
    URLS = getPDFs(pdfFiles)
    processPDFs()
    extractText()
    jsonData = []
    for i , data in enumerate(pdfFiles):
        jsonData.append(
            {
                "page-url":data,
                "pdf-url":URLS[i],
                "pdf-content":os.path.json(OUT_TXT_FILES,str(i))
            }
        )
    
    with open(OUTFILE,'w') as f:
        json.dump(jsonData, f,indent=4)
    
    