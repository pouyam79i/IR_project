import json
from typing import List
from hazm import Normalizer, Lemmatizer, word_tokenize

class SearchEngine:

    def __init__(self, index_addr:str, refined_db_addr:str, max_doc=12000, debug_mode=False) -> None:
        # class configs
        self.index_addr = index_addr
        self.refined_db_addr = refined_db_addr
        self.index = dict()
        self.DEBUG = debug_mode
        self.max_doc = max_doc
        # tools configs
        self.normalizer = Normalizer().normalize
        self.stemmer = Lemmatizer().lemmatize
        self.tokenizer = word_tokenize
        self.useless_notations = ['_' ,'-', '+', '*', '%', '$', '/', '.', '!', '(', ')', '^', '=', '<', '>', '?', '&', '@'
                                   '\\', ';', '\'', '\"', '{', '}', '[', ']', ':', '«', '»', ','] # useless notations

    # Loads Index File
    def __load_index(self):
        try:
            with open(self.index_addr, 'r', encoding='utf-8') as file:
                self.index = json.load(file)
                return True
        # File not found
        except FileNotFoundError:
            print("file not found in '{}'".format(self.index_addr))
        # Invalid json file
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
        # Other exceptions
        except Exception as e:
            print("error:", e)
        return False

    # Pre process queries
    def __query_processor(self, q:str) -> List[str]:
        nq = self.normalizer(q)
        rmun_nq = ''
        for i in nq:
            if i in self.useless_notations:
                rmun_nq = rmun_nq + ' '
            else:
                rmun_nq = rmun_nq + i
        tokens = self.tokenizer(rmun_nq)
        stemmed_tokens = []
        for i in range(len(tokens)):
            stem = self.stemmer(tokens[i])
            if len(stem) == 0:
                continue
            stemmed_tokens.append(stem)
        if self.DEBUG:
            print("purified query tokens: ", stemmed_tokens)
        return stemmed_tokens

    # Displays result of search
    def __display_results(self, res:List[str]):
        pass

    # scoring docs for a term
    def __score_tf_idf(self, term: str, doc_id: str) -> float:
        if self.index.get('term') == None: return 0
        tf = self.index['term']

    # search and rank here
    def __search(self, processed_q:List[str]) -> List[str]:
        pass

    # start search engine
    def run(self, test_q=''):
        if not self.__load_index(): return
        if test_q != '':
            purified_q = self.__query_processor(test_q)
            res = self.__search(purified_q)
            self.__display_results(res)
        else:
            q = ''
            while q.lower() != 'exit':
                q = input('Please Type Your Query: ')
                purified_q = self.__query_processor(q)
                res = self.__search(purified_q)
                self.__display_results(res)
        