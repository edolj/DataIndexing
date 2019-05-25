from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import os
import re

from models import Base, Indexword, Posting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URI = 'postgres+psycopg2://postgres:defugalo@localhost:5432/indexDB'
stop_words = set(stopwords.words('slovenian.txt'))


def preprocess_text(og_text):
    # 1. convert text to lowercase
    text = og_text.lower()

    # 2. remove numbers
    text = re.sub(r'\d+', '', text)

    # 3. remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # 4. stop words
    tokens = word_tokenize(text)
    return [i for i in tokens if not i in stop_words]


def indexes(array, check_word):
    ind_text = ''
    count = 0
    for i in array:
        if i == check_word:
            ind_text += str(count) + ','
        count += 1

    return ind_text


def delete_database():
    eng = create_engine(DATABASE_URI)
    Base.metadata.drop_all(eng)


def make_posting(searchedWord, result, file, session):

    exsists = False
    globalFreq = 0
    globalInds = ''

    words = searchedWord.split()
    for word in words:
        if word in result:
            exsists = True

            fdist = FreqDist(result)
            freqR = fdist[word]
            inds = indexes(result, word)

            globalFreq += freqR
            globalInds += inds

    if exsists:
        posting = Posting(
            word=searchedWord,
            documentName=file[3:],
            frequency=globalFreq,
            indexes=globalInds[:-1]
        )

        session.add(posting)
        session.commit()


if __name__ == "__main__":

    queryWords = ["predelovalne dejavnosti", "trgovina", "social services"]

    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    for word in queryWords:
        indexWord = Indexword(
            word=word
        )

        s.add(indexWord)
        s.commit()

    directory = "../data/"

    for filename in os.listdir(directory):
        if filename.endswith(".html"):

            og_text = ""
            file = directory + filename
            readFile = open(file, 'r').read()
            parser = BeautifulSoup(readFile, "html.parser")

            # remove all javascript and stylesheet code
            for script in parser(["script", "style", "meta"]):
                script.extract()

            # append html text to variable
            for string in parser.stripped_strings:
                og_text += string + "\n"

            # save preprocessed text to variable
            result = preprocess_text(og_text)

            for word in queryWords:
                make_posting(word, result, file, s)

    s.close()
