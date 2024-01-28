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
        self.db = dict()
        self.DEBUG = debug_mode
        self.max_doc = max_doc
        self.using_champions_allowed = False # it is not allowed by default
        self.champions_list = dict()         # TODO: it goes from a token to a few number of docs
        self.search_score_mode = 'tf_idf'
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
    
        # Loads Index File
    
    # Loads Refined DB
    def __load_refined_db(self):
        try:
            with open(self.refined_db_addr, 'r', encoding='utf-8') as file:
                self.db = json.load(file)
                return True
        # File not found
        except FileNotFoundError:
            print("file not found in '{}'".format(self.refined_db_addr))
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
    def __display_results(self, res:List[str], max_display_res=5):
        print("Search Results:")
        if len(res) == 0:
            print("no result found!")
            return
        count = 0
        for doc_id in res:
            if count >= max_display_res:
                return
            count += 1
            title = self.db[doc_id]['title']
            content = self.db[doc_id]['content']
            if len(content) > 100:
                content = content[:100] + '...'
            url = self.db[doc_id]['url']
            print('{} - Title: {}'.format(count, title))
            print(content.replace('\n', ' '))
            print(url.replace('\n', ' '))

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

    # scoring docs by cosine, vector based!
    def __score_cosine(self, vector_q:List[str], vector_q_len: float, vector_d:List[str], alpha:float=0.001)->float:
        vector_d_len = 0.0
        for i in vector_d:
            vector_d_len += math.pow(i, 2)
        vector_d_len = math.sqrt(vector_d_len)
        score = 0.0
        for i in range(len(vector_q)):
            score += (vector_q[i] * vector_d[i])
        dv = vector_d_len * vector_q_len + alpha 
        score /= dv
        return score
        
    # search and rank here
    def __search(self, processed_q:List[str], score_mode='tf_idf') -> List[str]:
        
        # set search index (?champions)
        if self.using_champions_allowed:
            index = self.champions_list
        else:
            index = self.index

        # searching only in related docs - index elimination        
        related_doc_id = []
        for term in processed_q:
            if index.get(term) == None:
                continue
            related_doc_id = self.__merge_postings(related_doc_id, list(index[term]['postings_list'].keys()))
        
        # using max heap to process faster the top k
        heap = []
        heapify(heap)
         
        # using cosine scoring.
        if score_mode=='cosine':
            # TODO: complete cosine mode
            pass

        # using tf*idf scoring. DEFAULT
        else:
            for doc_id in related_doc_id:
                score = 0.0
                for term in processed_q:
                    score = score + self.__score_tf_idf(term, doc_id)
                heappush(heap, (score * -1, doc_id))

        # extracting res
        res = []
        count = 0
        while count < 5 and len(heap) > 0:
            item = heappop(heap)
            if self.DEBUG and count < 5:
                print("{}-Doc_ID: {} - Score: {}".format(count, item[1], item[0] * -1))
            res.append(item[1])
            count += 1
        return res

    # this function updates champions list, then enables it -> so search engine will use champions list
    def enable_champions_list(self, x_most_related = 5):
        for term in self.index:
            postings = self.index[term]['postings_list']
            if len(list(postings.keys())) > x_most_related:
                heap = []
                heapify(heap)
                for doc_id in postings:
                    heappush(heap, (postings[doc_id] ,doc_id))
                extracted_top_docs = list()
                i = 0
                while i < x_most_related:
                    extracted_top_docs.append(int(heappop(heap)[1]))
                    i += 1
                # sort in-place
                extracted_top_docs.sort()
                new_postings = dict()
                for doc_id in extracted_top_docs:
                    new_postings[str(doc_id)] = postings[str(doc_id)] 
                self.champions_list[term] = {'freq':self.index[term]['freq'],'postings_list':new_postings}    
            else:
                self.champions_list[term] = {'freq':self.index[term]['freq'],'postings_list':postings}
        self.using_champions_allowed = True
        if self.DEBUG:
            with open('./debug_champions_list.json', 'w', encoding='UTF-8') as file:
                json.dump(self.champions_list, file, indent=2, ensure_ascii=False)
 
    # This function prevents search engine from using champions list -> makes it default use of index
    def disable_champions_list(self):
        self.using_champions_allowed = False
    
    # set score function
    def set_search_score_mode(self, mode='tf_idf'):
        self.search_score_mode = mode
        print('search mode set to \'{}\'. if not exist default is tf_idf'.format(mode))
    
    # start search engine
    def run(self, test_q='', max_display_res=5):
        if not self.__load_index(): return
        self.__load_refined_db()
        if test_q != '':
            purified_q = self.__query_processor(test_q)
            res = self.__search(purified_q, self.search_score_mode)
            self.__display_results(res, max_display_res)
        else:
            q = ''
            while q.lower() != 'exit':
                q = input('Please Type Your Query: ')
                purified_q = self.__query_processor(q)
                res = self.__search_tf_idf(purified_q)
                self.__display_results(res, max_display_res)
