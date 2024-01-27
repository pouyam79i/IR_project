from indexer import Indexer
from search_engine import SearchEngine

DEBUG = True

ENABLE_INDEXER = False
ENABLE_SEARCH = True

DB_ADDRESS = './IR_data_news_12k.json'
INDEX_ADDRESS = './index.json'
REFINED_DB_ADDRESS = './refined_db.json'

def main():

    my_indexer = Indexer(DB_ADDRESS, INDEX_ADDRESS, REFINED_DB_ADDRESS, 50, DEBUG)
    my_search_engine = SearchEngine(INDEX_ADDRESS, REFINED_DB_ADDRESS, 12000 ,DEBUG)

    if ENABLE_INDEXER: my_indexer.run()
    if ENABLE_SEARCH: my_search_engine.run(test_q='فوتبالی')

main()
