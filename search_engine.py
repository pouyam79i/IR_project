import json
from typing import List

class SearchEngine:

    def __init__(self, index_addr:str) -> None:
        self.index_addr = index_addr
        self.index = dict()

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
    def __query_processor(self):
        pass

    # Displays result of search
    def __display_results(res:List[str]):
        pass

    def __score_tf_idf(term: str) -> float:
        pass

    def __search(query:str) -> List[str]:
        pass

    # start search engine
    def run(self):
        if not self.__load_index(): return
        q = ''
        while q.lower() != 'exit':
            q = input('Please Type Your Query: ')
            purified_q = self.__query_processor(q)
            res = self.__search(purified_q)
            self.__display_results(res)
        