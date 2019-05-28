# DataIndexing

Okolje: MacOS, PyCharm, DB Browser for SQLite, Safari

Uporaba: Zaženi "indexer/program.py" 
(priporočljivo je bazo izbrisati, če ustvarjamo na novo)

Main funkcija programa vsebuje tri funkcije:
- data_indexing(): indeksira html datoteke in ustvari inverted index
- data_retrieval(string): s query iščemo po inverted index-u in vrnemo poizvedbo
- naive_data_retrieval(string): naivno iskanje besed po html datotekah
