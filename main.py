from indexer import Indexer
from search_engine import SearchEngine

ENABLE_INDEXER = False
ENABLE_SEARCH = True

DB_ADDRESS = './IR_data_news_12k.json'
INDEX_ADDRESS = 'index.json'

def main():

    my_indexer = Indexer(DB_ADDRESS, INDEX_ADDRESS)
    my_search_engine = SearchEngine(INDEX_ADDRESS)

    if ENABLE_INDEXER: my_indexer.run()
    if ENABLE_SEARCH: my_search_engine.run()

main()
