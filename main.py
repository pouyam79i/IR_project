from indexer import Indexer

ENABLE_INDEXER = False
ENABLE_SEARCH = True

DB_ADDRESS = './IR_data_news_12k.json'
INDEX_ADDRESS = 'index.json'

def main():

    my_indexer = Indexer(DB_ADDRESS, INDEX_ADDRESS)
    
    if ENABLE_INDEXER: my_indexer.run()
    if not ENABLE_SEARCH: return

    # TODO: add search engine here

main()
