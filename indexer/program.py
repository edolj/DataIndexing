from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os
import re

if __name__ == "__main__":

    og_text = ""

    directory = "../data/e-prostor.gov.si/"

    for filename in os.listdir(directory):
        if filename.endswith(".html"):

            file = directory + filename
            readFile = open(file, 'r').read()
            parser = BeautifulSoup(readFile, "html.parser")

            # remove all javascript and stylesheet code
            for script in parser(["script", "style"]):
                script.extract()

            # append html text to variable
            for string in parser.stripped_strings:
                og_text += string + "\n"

    # PREPROCESSING

    # 1. convert text to lowercase
    text = og_text.lower()

    # 2. remove numbers
    text = re.sub(r'\d+', '', text)

    # 3. remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # 4. stop words
    stop_words = set(stopwords.words('slovenian.txt'))
    tokens = word_tokenize(text)
    result = [i for i in tokens if not i in stop_words]
    print(result)

