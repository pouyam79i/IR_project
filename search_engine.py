import json, math
from typing import List
from hazm import Normalizer, Lemmatizer, word_tokenize
from heapq import heappop, heappush, heapify

class SearchEngine:

    def __init__(self, index_addr:str, refined_db_addr:str, max_doc:float=12000, debug_mode=False) -> None:
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

    # use this for merging to list and remaining the orders
    def __merge_postings(self, list1:List[str], list2:List[str]):
        ans = []
        if len(list1) != 0: item1 = list1.pop(0)
        if len(list2) != 0: item2 = list2.pop(0)
        while len(list1) != 0 and len(list2) != 0:
            if int(item1) > int(item2):
                ans.append(item2)
                item2 = list2.pop(0)
            elif int(item1) < int(item2):
                ans.append(item1)
                item1 = list1.pop(0)
            else:
                ans.append(item1)
                item1 = list1.pop(0)
                item2 = list2.pop(0)
        if len(list1) != 0:
            ans.extend(list1)
        elif len(list2) != 0:
            ans.extend(list2)
        return ans
    
    # scoring docs for a term
    def __score_tf_idf(self, term: str, doc_id: str) -> float:
        if self.index.get(term) == None:
            # if self.DEBUG: print("No such term '{}' in index.".format(term))
            return 0 # no such term exists in our index file
        if self.index[term]['postings_list'].get(doc_id) == None:
            # if self.DEBUG: print("No such index={} for term: {}".format(doc_id, term))
            return 0 # there is no such term in this doc
        else:
            tf = math.log10(1 + self.index[term]['postings_list'][doc_id])
        df = len(list(self.index[term]['postings_list'].keys()))
        idf = math.log10(self.max_doc/df)
        # if self.DEBUG: print("for term'{}' and doc:{} tf={}, idf={}".format(term, doc_id, tf, idf))
        return tf*idf

    # search and rank here
    def __search_tf_idf(self, processed_q:List[str]) -> List[str]:
        # searching only in related docs
        related_doc_id = []
        for term in processed_q:
            if self.index.get(term) == None:
                continue
            related_doc_id = self.__merge_postings(related_doc_id, list(self.index[term]['postings_list'].keys()))
        # using max heap to process faster the top k
        heap = []
        heapify(heap) 
        for doc_id in related_doc_id:
            score = 0.0
            for term in processed_q:
                score = score + self.__score_tf_idf(term, doc_id)
            heappush(heap, (score * -1, doc_id))
        res = []
        count = 0
        while count < 10 and len(heap) > 0:
            item = heappop(heap)
            if self.DEBUG and count < 10:
                print("{}-Doc_ID: {} - Score: {}".format(count, item[1], item[0] * -1))
            res.append(item[1])
            count += 1
        return res

    # start search engine
    def run(self, test_q=''):
        if not self.__load_index(): return
        if test_q != '':
            purified_q = self.__query_processor(test_q)
            res = self.__search_tf_idf(purified_q)
            self.__display_results(res)
        else:
            q = ''
            while q.lower() != 'exit':
                q = input('Please Type Your Query: ')
                purified_q = self.__query_processor(q)
                res = self.__search_tf_idf(purified_q)
                self.__display_results(res)
        