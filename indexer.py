import json
from typing import List
from heapq import heappop, heappush, heapify
from hazm import Normalizer, Lemmatizer, word_tokenize

# This is the indexer class
# It handles everything related to indexing!
class Indexer:

    # Initializer index
    def __init__(self, load_addr:str, save_addr:str, refined_db_addr:str, remove_x_sw:int, enable_normalizer:bool=True, debug_mode = False) -> None:
        # Indexer config
        self.load_addr = load_addr
        self.save_addr = save_addr
        self.refined_db_addr = refined_db_addr
        self.remove_x_sw = remove_x_sw              # remove x most frequent words
        self.db = None                              # loading db into db
        self.refined_db = dict()                    # after reading db - we create refined from docs
        self.index = dict()                         # building index using dict as base data structure
        self.enable_normalizer = enable_normalizer  # enabling normalizer
        self.DEBUG = debug_mode         
        
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
            count = 0
            with open(self.load_addr, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.db = dict()
                for id in data:
                    self.db[id] = {
                        "content" : data[id]['content'],
                    }
                    shortened_content = ''
                    if len(data[id]['content']) > 200:
                        shortened_content = data[id]['content'][:200] + '...'
                    else:
                        shortened_content = data[id]['content']
                    self.refined_db[id] = {
                        "title": data[id]['title'],
                        "content" : shortened_content ,
                        "url" : data[id]['url'],
                        "t_count": 0
                    }
                    count += 1
                print('Max Docs:', count)
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
            json.dump(self.index, file, indent=2, ensure_ascii=False)

        with open(self.refined_db_addr, 'w', encoding='UTF-8') as file2:
            json.dump(self.refined_db, file2, indent=2, ensure_ascii=False)

    # Normalizer is used to process contents and normalizing the text for that content 
    def __normalizer(self, content:str) -> str:
        if not self.enable_normalizer: return content
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

        max_element = len(heap)
        if self.DEBUG and self.remove_x_sw >= 10 : print('Here you can see 10 first stop words:')
        for i in range(self.remove_x_sw):
            if i >= max_element:
                return
            item = heappop(heap)
            if self.DEBUG and i < 10:
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
            tks = self.__tokenizer(content)
            new_tokens = []
            # Third: Stemming the tokens
            for t in tks:
                stem = self.__stemmer(t)
                if stem == '':
                    continue
                new_tokens.append(stem)

            self.refined_db[id]['t_count'] = len(new_tokens)

            # Forth: Appending new tokens to the tokens list
            for item in new_tokens:
                if item == '':
                    continue
                tokens.append({'doc_id': id, 'token':item})
        
        # Test Area
        if self.DEBUG:
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
        
        if self.DEBUG:
            print("Number of extracted terms in dict: {}".format(len(list(self.index.keys()))))

        # ####################### end of indexing

    # set normalizer
    def set_enable_normalizer(self, enable_normalizer:bool=True):
        self.enable_normalizer = enable_normalizer
        
    # Run the indexer
    def run(self):
        self.__load_db()
        if self.db is None: 
            return
        self.__indexer_engine()
        self.__save_index()
