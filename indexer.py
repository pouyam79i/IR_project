import json
from typing import List
from heapq import heappop, heappush, heapify
from hazm import Normalizer, Lemmatizer, word_tokenize

DEBUG = True

# This is the indexer class
# It handles everything related to indexing!
class Indexer:

    # Initializer index
    def __init__(self, load_addr:str, save_addr:str, remove_x_sw:int) -> None:
        # Indexer config
        self.load_addr = load_addr
        self.save_addr = save_addr
        self.remove_x_sw = remove_x_sw  # remove x most frequent words
        self.db = None                  # loading db into db
        self.index = dict()             # building index using dict as base data structure
        
        # setup tools here
        self.normalizer = Normalizer().normalize
        self.stemmer = Lemmatizer().lemmatize
        self.tokenizer = word_tokenize
        self.useless_notations = ['_' ,'-', '+', '*', '%', '$', '/', '.', '!', '(', ')', '^', '=', '<', '>', '?', '&', '@'
                                   '\\', ';', '\'', '\"', '{', '}', '[', ']', ':', '«', '»', ','] # useless notations
        self.stop_words = []

    # Load Database (a json files here)
    def __load_db(self):
        try:
            with open(self.load_addr, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.db = dict()
                for id in data:
                    self.db[id] = {
                        "content" : data[id]['content'],
                        "url" : data[id]['url']
                    }
                return
        # File not found
        except FileNotFoundError:
            print("file not found in {}".format(self.load_addr))
        # Invalid json file
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
        # Other exceptions
        except Exception as e:
            print("error:", e)
        self.db = None       

    # Save index file
    def __save_index(self):
        with open(self.save_addr, 'w', encoding='UTF-8') as file:
            json.dump(self.index, file, indent=4, ensure_ascii=False)

    # Normalizer is used to process contents and normalizing the text for that content 
    def __normalizer(self, content:str) -> str:
        content = self.normalizer(content)
        res = ''
        for c in content:
            if c in self.useless_notations:
                res = res + ' '
            else:
                res = res + c
        return res

    # This function is used for tokenization
    def __tokenizer(self, content:str)->List[str]:
        return self.tokenizer(content)

    # This function is used for stemming
    def __stemmer(self, term:str) -> str:
        stem = self.stemmer(term)
        if len(stem) == 0:
            # return term
            return ''
        else: 
            return stem

    # Use this function to extract you stop word list!
    # You can disable this feature!
    def __remove_sw(self):
        heap = []
        heapify(heap)
        for term in list(self.index.keys()):
            heappush(heap, (-1 * int(self.index[term]['freq']), term))

        for i in range(self.remove_x_sw):
            item = heappop(heap)
            if DEBUG and i < 10:
                print("{}-term: {}, freq: {}".format(i, item[1], item[0] * -1))
            self.index.pop(item[1])

    # Do indexing operation here
    def __indexer_engine(self):

        # *********************** This are is for tokenization process:
        tokens = []
        for id in self.db:
            # First: Normalize Content
            content = self.__normalizer(self.db[id]['content'])
            
            # Second: Tokenizing
            new_tokens = self.__tokenizer(content)
           
            # Third: Stemming the tokens
            for i in range(len(new_tokens)):
                new_tokens[i] = self.__stemmer(new_tokens[i])

            # Forth: Appending new tokens to the tokens list
            for item in new_tokens:
                if item == '':
                    continue
                tokens.append({'doc_id': id, 'token':item})
        
        # Test Area
        if DEBUG:
            print("first 10 Stop Words to remove: ", self.stop_words[:10])
            if len(tokens) >= 10:
                print("Some of tokens ready to index:", tokens[:10])
            else:
                print("Some of tokens ready to index:", tokens)

        # *********************** end of tokenization
        
        # ####################### This are is for indexing process:
        for item in tokens:
            doc_id = item['doc_id']
            token = item['token']
            if token in self.index:
                temp_obj = self.index[token]
                new_freq = temp_obj['freq'] + 1
                postings_list = temp_obj['postings_list']
                if doc_id not in postings_list:
                    postings_list[doc_id] = 1
                else:
                    postings_list[doc_id] = postings_list[doc_id] + 1
                self.index[token]['freq'] = new_freq
                self.index[token]['postings_list'] = postings_list
            else:
                # we have a term freq - and term/doc freq in postings
                self.index[token] = {'freq': 1, 'postings_list': {doc_id:1}}

        # remove X most frequent words
        if self.remove_x_sw > 0:
            self.__remove_sw()

        # sorting dictionary by term
        self.index = dict(sorted(self.index.items()))
        # ####################### end of indexing

    # Run the indexer
    def run(self):
        self.__load_db()
        if self.db is None: 
            return False
        self.__indexer_engine()
        self.__save_index()
        return True
