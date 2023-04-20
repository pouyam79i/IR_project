# Coded by Pouya Mohammadi
# query handler code
# importing libs
import json
import os
from colorama import Fore, Back, Style

# running app
os.system('cls' if os.name == 'nt' else 'clear')
print(Fore.GREEN + "Booting Query Handler..." + Style.RESET_ALL)

# global vars
raw_data = {}
pi = {}  #positional index - result of previous parts!

# reading data files
with open('json/IR_data_news_12k.json', 'r', encoding='utf-8') as data_file:
    raw_data = json.load(data_file)
with open('json/positional_indexing_result.json', 'r', encoding='utf-8') as data_file:
    pi = json.load(data_file)


# this class contain boolean model search algorithms
# each function accepts posting lists
class BooleanModel:
    def __init__(self) -> None:
        pass

    # handles and operations
    def and_ops(p1 = [], p2 = []):
        ans = []
        while len(p1) != 0 and len(p2) != 0:
            docID1 = int(p1[0])
            docID2 = int(p2[0]) 
            if docID1 == docID2:
                ans.append(docID1)
                p1.pop(0)
                p2.pop(0)
            elif docID2 > docID1:
                p1.pop(0)
            else:
                p2.pop(0)
        return ans

    # handles or operations
    def or_ops(p1 = [], p2 = []):
        # 'both' and 'one' partition will be used for ranking!
        ans = {'both':[], 'one':[]}
        while len(p1) != 0 and len(p2) != 0:
            docID1 = int(p1[0])
            docID2 = int(p2[0]) 
            if docID1 == docID2:
                ans['both'].append(docID1)
                p1.pop(0)
                p2.pop(0)
            elif docID2 > docID1:
                ans['one'].append(docID1)
                p1.pop(0)
            else:
                ans['one'].append(docID2)
                p2.pop(0)
        return ans

    # handles not operations
    def not_ops(p = [], not_p = [], mode='or'):
        not_p = [int(i) for i in not_p]         # it is most likely to be string value
        ans = []
        # on or result check!
        if mode == 'or':
            ans = {'both':[], 'one':[]}
            both = p['both']
            one = p['one']
            # for both
            while len(both) != 0:
                item = int(both.pop(0))
                if item not in not_p:
                    ans['both'].append(item)
            # for one
            while len(one) != 0:
                item = one.pop(0)
                if item not in not_p:
                    ans['one'].append(item)
        # any other result check
        else:
            while len(p) != 0:
                item = p.pop(0)
                if item not in not_p:
                    ans.append(item)
            

# this class parse the input query and use BooleanModel to find result
# TODO: so for it works only with docIDs - we have nothing to do with termIDs
class QueryAnalyzer:
    def __init__(self) -> None:
        pass
    
    # TODO: parsing query for BooleanModel
    def queryParser(raw_query = ''):
        pass

    # tries to build p lists for the parsed query
    # TODO: 'or' search logic is not implemented. right now we have only 'and' and 'or'
    def termPListExtractor(parsed_query = {'and':[], 'or':[], 'not':[]}):
        freq = []       # keep track of frequency of terms
        and_p_list = []
        or_p_list = []
        not_p_list = []
        # gathering 'and' terms postings list
        for item in parsed_query['and']:
            info = pi[item]
            if info is None:
                print(Fore.RED + "No such a term as {}!".format(item) + Style.RESET_ALL)
                continue
            freq.append(int(info['freq']))
            and_p_list.append(info['docIDs'].keys())
            # min sort
            i = range(len(freq))
            while i > 1:
                i -= 1
                if freq[i] < freq[i-1]:
                    temp = freq[i]
                    freq[i] = freq[i-1]
                    freq[i-1] = temp
                    temp = and_p_list[i] 
                    and_p_list[i] = and_p_list[i-1]
                    and_p_list[i-1] = temp
                else:
                    break

        # gathering 'not' terms postings list - 
        res_set = set()
        for item in parsed_query['not']:
            docIDs = pi[item]['docIDs'].keys()
            for id in docIDs:
                res_set.add(id)
        not_p_list = list(res_set)

        return {'and':and_p_list, 'or': or_p_list, 'not':not_p_list}

    # TODO: search over database and return results!
    def search(termPList = {'and':[], 'or':[], 'not':[]}):
        pass


# query handler
os.system('cls' if os.name == 'nt' else 'clear')
while True:
    inVal = str(input(Fore.BLUE + 'Insert Query:'))
    if inVal.upper() == 'EXIT':
        break
    if inVal == 'clear' or inVal == 'cls':
        os.system('cls' if os.name == 'nt' else 'clear')
        continue
    # TODO: add analyzer here


print("Query Handler is Shutdown!")
