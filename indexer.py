import json
# from hazm.utils import stopwords_list
from hazm import Normalizer, Stemmer, word_tokenize, stopwords_list

DEBUG = False

# This is the indexer class
# It handles everything related to indexing!
class Indexer:

    # Initializer index
    def __init__(self, load_addr:str, save_addr:str) -> None:
        # Indexer config
        self.load_addr = load_addr
        self.save_addr = save_addr
        self.db = None                # loading db into db
        self.index = dict()             # building index using dict as base data structure
        
        # setup tools here
        self.normalizer = Normalizer().normalize
        self.stemmer = Stemmer().stem
        self.tokenizer = word_tokenize
        self.useless_notations = ['_' ,'-', '+', '*', '%', '$', '/', '.', '!', '(', ')', '^', '\\', ';', '\'', '\"', '{', '}', '[', ']', ',', ':'] # hashtag is useful
        self.stop_words = stopwords_list()[:50]

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

    # Do indexing operation here
    def __indexer_engine(self):

        # *********************** This are is for tokenization process:
        tokens = []
        for id in self.db:
            # First: Normalize Content
            content = self.normalizer(self.db[id]['content'])
            # Also: remove useless notations
            temp = content
            content = ''
            for i in temp:
                if i in self.useless_notations:
                    continue
                content = content + i

            # Second: Tokenizing
            new_tokens = self.tokenizer(content)
           
            # Third: remove stop words
            non_sw_new_tokens = []
            for i in new_tokens:
                if i in self.stop_words or i in self.useless_notations or len(i) == 0:
                    continue
               
                # Forth: stem the word
                stem = self.stemmer(i)
                if len(stem) == 0:
                    continue

                # Purified tokens
                non_sw_new_tokens.append({"doc_id":id, "token":stem})

            tokens.extend(non_sw_new_tokens)
        
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
                    postings_list.append(doc_id)
                self.index[token]['freq'] = new_freq
                self.index[token]['postings_list'] = postings_list
            else:
                self.index[token] = {'freq': 1, 'postings_list': [doc_id]}

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
