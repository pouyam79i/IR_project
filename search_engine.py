import json

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

    def __query_processor(self):
        pass

    # start search engine
    def run(self):
        if not self.__load_index(): return

        