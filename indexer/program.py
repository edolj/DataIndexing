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


def indexes(array, check_word):
    ind_text = ''
    count = 0
    for i in array:
        if i == check_word:
            ind_text += str(count) + ','
        count += 1

    return ind_text[:-1]


def recreate_database(eng):
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)


if __name__ == "__main__":

    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    '''
    posting = Posting(
        word='trgovina',
        documentName='prodaja',
        frequency=15,
        indexes='1,2,3,4'
    )
  
    indexWord = Indexword(
        word='trgovina'
    )
    
    s.add(indexWord)
    s.commit()
    s.close()
    '''

    stop_words = set(stopwords.words('slovenian.txt'))

    directory = "../data/e-prostor.gov.si/"

    for filename in os.listdir(directory):
        if filename.endswith(".html"):

            og_text = ""
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
            tokens = word_tokenize(text)
            result = [i for i in tokens if not i in stop_words]

            # end

            word = 'arhiv'
            if word in result:
                fdist = FreqDist(result)
                freqR = fdist[word]
                inds = indexes(result, word)

                posting = Posting(
                    word=word,
                    documentName=file,
                    frequency=freqR,
                    indexes=inds
                )

                s.add(posting)
                s.commit()

    s.close()

