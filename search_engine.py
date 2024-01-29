import json, math, time
from typing import List
from hazm import Normalizer, Lemmatizer, word_tokenize
from heapq import heappop, heappush, heapify

class SearchEngine:

    def __init__(self, index_addr:str, refined_db_addr:str, enable_normalizer:bool=True, debug_mode:bool=False) -> None:
        # class configs
        self.index_addr = index_addr
        self.refined_db_addr = refined_db_addr
        self.index_is_loaded = False
        self.index = dict()
        self.db = dict()
        self.DEBUG = debug_mode
        self.max_doc = 1000
        self.enable_normalizer = enable_normalizer
        self.using_champions_allowed = False # it is not allowed by default
        self.champions_list = dict()         # TODO: it goes from a token to a few number of docs
        self.search_score_mode = 'tf_idf'
        self.max_display_res = 5
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
                self.max_doc = len(list(self.db.keys()))
                if self.DEBUG:
                    print("Max Doc:{}".format(self.max_doc))
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
        nq = self.normalizer(q) if self.enable_normalizer else q
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
        print("Search Results:")
        if len(res) == 0:
            print("no result found!")
            return
        count = 0
        for doc_id in res:
            if count >= self.max_display_res:
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
    # alpha is smoother
    def __score_cosine(self, vector_q:List[float], vector_q_len: float, vector_d:List[float], alpha:float=0.001)->float:
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
    # alpha is smoother
    def __search(self, processed_q:List[str], score_mode='tf_idf', alpha:float=0.001) -> List[str]:
        
        # set search index (?champions)
        if self.using_champions_allowed:
            index = self.champions_list
        else:
            index = self.index
        
        start_time = time.time()
        
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
            q_vec = []
            for term in processed_q:
                if index.get(term) != None:
                    idf = math.log(self.max_doc/(1 + len(list(index[term]['postings_list'].keys())))) + alpha
                else:
                    idf = alpha
                q_vec.append(idf)
            
            q_vec_len = 0
            for item in q_vec:
                q_vec_len += math.pow(item, 2)
            q_vec_len = math.sqrt(q_vec_len)     
            
            for doc_id in related_doc_id:
                d_vec = []
                for term in processed_q:
                    if index.get(term) != None:
                        if index[term]['postings_list'].get(doc_id) != None:
                            tf = math.log10(1 + index[term]['postings_list'][doc_id]) + alpha
                        else:
                            tf = alpha
                    else:
                        tf = alpha
                    d_vec.append(tf)
                score = self.__score_cosine(q_vec, q_vec_len, d_vec, alpha)
                heappush(heap, (score * -1, doc_id))

        # using tf*idf scoring. DEFAULT
        else:
            for doc_id in related_doc_id:
                score = 0.0
                for term in processed_q:
                    score = score + self.__score_tf_idf(term, doc_id)
                heappush(heap, (score * -1, doc_id))
        
        stop_time = time.time()
        
        # extracting res
        res = []
        count = 0
        while len(heap) > 0:
            item = heappop(heap)
            if self.DEBUG and count < 5:
                print("{}-Doc_ID: {} - Score: {}".format(count, item[1], item[0] * -1))
            res.append(item[1])
            count += 1
        if self.DEBUG:
            print("{} results in {} seconds:".format(len(res), stop_time - start_time))
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
    
    # set max display res
    def set_max_display_res(self, max_display_res:int):
        if max_display_res <= 0:
            self.max_display_res = 1
        else:
            self.max_display_res = max_display_res
    
    # start search engine
    def run(self):
        print("Running search engine...")
        if not self.__load_index():
            if self.DEBUG:
                print("Failed to run search engine.")
                return
        self.__load_refined_db()
        self.index_is_loaded = True
        print("Engine is up.") 
    
    # use this function to search
    def search(self, query=''):
        if not self.index_is_loaded:
            print('Please run() engine first!')
            return
        if query != '':
            purified_q = self.__query_processor(query)
            res = self.__search(purified_q, self.search_score_mode)
            self.__display_results(res)
        else:
            q = ''
            while q.lower() != 'exit':
                q = input('Please Type Your Query: ')
                purified_q = self.__query_processor(q)
                res = self.__search(purified_q)
                self.__display_results(res)
