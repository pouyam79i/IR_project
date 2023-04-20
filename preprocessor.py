# Coded by Pouya Mohammadi
# preprocessor code
# Importing Libs
import os
import json
from parsivar import Normalizer
from parsivar import Tokenizer
from parsivar import FindStems

# running app
os.system('cls' if os.name == 'nt' else 'clear')

# global vars
punctuations = '!()-[]{};:\'\\"`,<>./?@#$%^&*_~+,،'
stopWords = ['و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'برای', 'آن', 'خود', 'تا', 'کرد', 'بر', 'هم', 'نیز', 'وی', 'اما', 'یا', 'هر']
contents = {}
positional_indexed = {}

# loading files
with open('json/IR_data_news_12k.json', 'r', encoding='utf-8') as data_file:
    contents = json.load(data_file)
docID = contents.keys()
# TODO: copying all data just in case - UNCOMMENT IF NEEDED
# all_data = contents
print("No-Process Test: ")
print(contents['0']['content'], end='\n\n')



# ******* Normalizer
# creating normalizer
normalizer = Normalizer()
for id in docID:
    contents[id]['content'] = normalizer.normalize(contents[id]['content'])
# Testing tokenizer
print("Normalizer Test: ")
print(contents['0']['content'], end='\n\n')



# ******* Cleaner Section
# removing punctuations
for id in docID:
    for letter in contents[id]['content']:
        if letter in punctuations:
            contents[id]['content'] = contents[id]['content'].replace(letter, " ")
print("Cleaner Test: ")
print(contents['0']['content'], end='\n\n')



# ******* Processor Section
# creating tokenizer
tokenizer = Tokenizer()
# tokenizing all words (contents are normalized before that)
for id in docID:
    contents[id]['content'] = tokenizer.tokenize_words(contents[id]['content'])
# Testing tokenizer
print("Tokenizer Test: ")
print(contents['0']['content'], end='\n\n')



# ******* Stop Word Removal Section
# removing stop words
for id in docID:
    tokenized_without_sw = []
    for word in contents[id]['content']:
        if word not in stopWords:
            tokenized_without_sw.append(word)
    contents[id]['content'] = tokenized_without_sw
# Testing stop word remover
print("Stop Word Removal Test: ")
print(contents['0']['content'], end='\n\n')



# ******* Stem Section
# finding steps
# dict['word'] = 'stem'
stemmer = FindStems()
for id in docID:
    for index in range(len(contents[id]['content'])):
        contents[id]['content'][index] = stemmer.convert_to_stem(contents[id]['content'][index])
# Testing stemmer
print("Stemmer Test: ")
print(contents['0']['content'], end='\n\n')



# ******* Positional Indexer Section
# positional indexing
for id in docID:
    position = 0
    for term in contents[id]['content']:
        if term not in positional_indexed.keys():
            positional_indexed[term] = {'freq':1}
        else:
            positional_indexed[term]['freq'] = positional_indexed[term]['freq'] + 1
        if id not in positional_indexed[term].keys():
            positional_indexed[term][id] = [position]
        else:
            positional_indexed[term][id].append(position)
        position += 1
# sorting by terms:
myKeys = list(positional_indexed.keys())
myKeys.sort()
sorted_dict = {i: positional_indexed[i] for i in myKeys}
positional_indexed = sorted_dict
# testing indexer:
print("Indexer Test: ")
limiter = 0
for term in positional_indexed:
    limiter += 1
    print('\'{}\':'.format(term))
    print(positional_indexed[term], end='\n\n')
    if limiter >= 1:
        break



# ******* Exporter Section
with open("json/positional_indexing_result.json", "w", encoding='utf-8') as write_file:
    json.dump(positional_indexed, write_file, indent=4)
