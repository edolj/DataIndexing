from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import os
import re
import sqlite3

conn = sqlite3.connect('inverted-index.db')
c = conn.cursor()

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


def test_merging_query(searchedWord, result, file):

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
        values = (searchedWord,
                  file[3:],
                  globalFreq,
                  globalInds[:-1])

        c.execute("""INSERT INTO Posting VALUES (?, ?, ?, ?)""", values)
        conn.commit()


def data_retrieval():
    print("Data retrieve from sql db.")


def naive_data_retrieval():
    print("Read each file.")


if __name__ == "__main__":

    c.execute('''CREATE TABLE IF NOT EXISTS IndexWord (
                        word TEXT PRIMARY KEY
                        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS Posting (
                        word TEXT NOT NULL,
                        documentName TEXT NOT NULL,
                        frequency INTEGER NOT NULL,
                        indexes TEXT NOT NULL,
                        PRIMARY KEY(word, documentName),
                        FOREIGN KEY (word) REFERENCES IndexWord(word)
                    );''')

    conn.commit()

    queryWords = ["predelovalne", "dejavnosti", "trgovina", "social", "services", "arhiv", "davek"]

    for word in queryWords:
        c.execute("""INSERT INTO IndexWord VALUES (?)""", (word,))
        conn.commit()

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

            # extract and append html text to variable (or get_text())
            for string in parser.stripped_strings:
                og_text += string + "\n"

            # save preprocessed text to variable
            result = preprocess_text(og_text)

            for word in queryWords:
                if word in result:
                    fdist = FreqDist(result)
                    freqR = fdist[word]
                    inds = indexes(result, word)

                    values = (word,
                              file[3:],
                              freqR,
                              inds)

                    c.execute("""INSERT INTO Posting VALUES (?, ?, ?, ?)""", values)
                    conn.commit()

    # r = conn.execute("""SELECT * FROM Posting""")
    # print(r.fetchall())
