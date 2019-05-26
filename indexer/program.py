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


def print_output(array):
    print("Frequencies  Document                                      Snippet")
    print("------------ --------------------------------------------- --------------------------------------------")

    for i in array:
        # logika za pridobivanje snippeta
        inds = i[3].split(",")
        firstSnippetIndex = int(inds[0])

        og_text = ""
        file = "../"+i[1]
        readFile = open(file, 'r').read()
        parser = BeautifulSoup(readFile, "html.parser")

        # remove all javascript and stylesheet code
        for script in parser(["script", "style", "meta"]):
            script.extract()

        # extract and append html text to variable (or get_text())
        for string in parser.stripped_strings:
            og_text += string + "\n"

        tokens = preprocess_text(og_text)

        snippet = "..." + tokens[firstSnippetIndex-2]+" "+tokens[firstSnippetIndex-1]+" "+tokens[firstSnippetIndex] \
                   + " " + tokens[firstSnippetIndex+1] + " " + tokens[firstSnippetIndex+2] + "..."

        # izpis podatkov v tabelo
        print(str(i[2]) + "            " + i[1] + "                   " + snippet)

def data_retrieval(queryWord):
    print("Results for a query: \"" + queryWord + "\"")
    print()

    if len(queryWord.split()) == 1:
        value = (queryWord.lower(),)
        r = conn.execute("""SELECT * FROM Posting WHERE word = ? ORDER BY frequency DESC""", value)
        outputs = r.fetchall()

        print_output(outputs)
    else:
        value = queryWord.lower().split()
        r = conn.execute("""SELECT * FROM Posting WHERE word IN (%s) ORDER BY frequency DESC""" % ("?," * len(value))[:-1], value)
        outputs = r.fetchall()

        # merging list
        mergedList = []
        for i in outputs:
            for j in outputs:
                if i != j and i[1] == j[1]:
                    mergedList.append((i[0]+" "+j[0], i[1], i[2]+j[2], (i[3]+j[3])[:-1]))
                    outputs.remove(j)
                    outputs.remove(i)

        for i in outputs:
            mergedList.append(i)

        # sort by frequencies and descend order
        sortedOutput = sorted(mergedList, key=lambda x: x[2], reverse=True)
        print_output(sortedOutput)


def naive_data_retrieval():
    print("Read each file.")


def data_indexing(queryWords):
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


if __name__ == "__main__":

    queryWords = ["trgovina", "davek", "predelovalne", "dejavnosti", "social", "services", "arhiv", "sistem", "spot"]
    data_indexing(queryWords)

    data_retrieval("social services")

