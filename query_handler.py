# Coded by Pouya Mohammadi
# query handler code
# importing libs
import json
import os
from colorama import Fore, Back, Style
from parsivar import FindStems

# running app
os.system('cls' if os.name == 'nt' else 'clear')
print(Fore.GREEN + "Booting Query Handler..." + Style.RESET_ALL)

# global vars
raw_data = {}
pi = {}  #positional index - result of previous parts!
stopWords = ['و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'برای', 'آن', 'خود', 'تا', 'کرد', 'بر', 'هم', 'نیز', 'وی', 'اما', 'یا', 'هر', 'ویا', '', 'ها', 'های']

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
    def and_ops(self, p1 = [], p2 = []):
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
    def or_ops(self, p1 = [], p2 = []):
        # 'both' and 'one' partition will be used for ranking!
        ans = list()
        while len(p1) != 0 and len(p2) != 0:
            docID1 = int(p1[0])
            docID2 = int(p2[0]) 
            if docID1 == docID2:
                ans.append(docID1)
                p1.pop(0)
                p2.pop(0)
            elif docID2 > docID1:
                ans.append(docID1)
                p1.pop(0)
            else:
                ans.append(docID2)
                p2.pop(0)
        return ans

    # handles not operations
    def not_ops(self, p = [], not_p = []):
        if len(not_p) == 0:
            return [int(i) for i in p]
        not_p = [int(i) for i in not_p]         # it is most likely to be string value
        ans = []
        # on or result check!
        # if mode == 'or':
        #     ans = {'both':[], 'one':[]}
        #     both = p['both']
        #     one = p['one']
        #     # for both
        #     while len(both) != 0:
        #         item = int(both.pop(0))
        #         if item not in not_p:
        #             ans['both'].append(item)
        #     # for one
        #     while len(one) != 0:
        #         item = one.pop(0)
        #         if item not in not_p:
        #             ans['one'].append(item)
        # # any other result check
        # else:
        while len(p) != 0:
            item = int(p.pop(0))
            if item not in not_p:
                ans.append(item)
        return ans
            

# this class parse the input query and use BooleanModel to find result
class QueryAnalyzer:
    def __init__(self) -> None:
        self.search_history = [] 
    
    # parsing query for BooleanModel
    def queryParser(self, raw_query = ''):
        self.search_history.append(raw_query)
        parsed_query = {'and':set(), 'or':set(), 'not':set()}
        stemmer = FindStems()
        # extracting must words!
        must_words = []
        on_save = False
        terms = ''
        next_raw_query = raw_query
        for i in range(len(raw_query)):
            if not on_save and raw_query[i] == '\"':
                on_save = True
            elif on_save and raw_query[i] == '\"':
                on_save = False
                must_words.append(terms)
                next_raw_query = next_raw_query.replace('\"' + terms + '\"', '')
                terms = ''
            elif on_save:
                terms += raw_query[i]
        for terms in must_words:
            for t in terms.split(' '):
                t = stemmer.convert_to_stem(t)
                if t not in stopWords:
                    parsed_query['and'].add(t)
        raw_query = next_raw_query
        # extracting 'not' words
        temp_split = raw_query.split(' ')
        raw_query = []
        not_flag = False
        for t in temp_split:
            t = stemmer.convert_to_stem(t)
            if t == '!':
                not_flag = True
            elif not_flag:
                not_flag = False
                if t not in stopWords:
                    parsed_query['not'].add(t)
                    if t in parsed_query['and']:
                        parsed_query['and'].remove(t)
            else:
                if t not in stopWords:
                    raw_query.append(t)
        # extracting 'or' words
        for t in raw_query:
            t = stemmer.convert_to_stem(t)
            if t not in parsed_query['and'] and t not in parsed_query['not']:
                parsed_query['or'].add(t)
        # returning parsed query
        res = {'and':[], 'or':[], 'not':[]}
        res['and'] = list(parsed_query['and'])
        res['or'] = list(parsed_query['or'])
        res['not'] = list(parsed_query['not'])
        return res

    # tries to build p lists for the parsed query
    def termPListExtractor(self, parsed_query = {'and':[], 'or':[], 'not':[]}):
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
            i = len(freq)
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
        # gathering 'or' terms postings list
        for item in parsed_query['or']:
            info = pi[item]
            if info is None:
                print(Fore.RED + "No such a term as {}!".format(item) + Style.RESET_ALL)
                continue
            freq.append(int(info['freq']))
            and_p_list.append(info['docIDs'].keys())
            # min sort
            i = len(freq)
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
        # gathering 'not' terms postings list  
        res_set = set()
        for item in parsed_query['not']:
            info = pi[item]
            if info is None:
                print(Fore.RED + "No such a term as {}!".format(item) + Style.RESET_ALL)
                continue
            docIDs = info['docIDs'].keys()
            for id in docIDs:
                res_set.add(id)
        not_p_list = list(res_set)

        return {'and':and_p_list, 'or': or_p_list, 'not':not_p_list}

    # search over database and return results!
    def search(self, termPList = {'and':[], 'or':[], 'not':[]}):
        emptyAnd = True
        res = []
        if len(termPList['and']) > 0:
            emptyAnd = False
            res_and = list(termPList['and'].pop(0))
            boolModel = BooleanModel()
            while len(termPList['and']) != 0:
                p2 = list(termPList['and'].pop(0))
                res_and = boolModel.and_ops(res_and, p2)
            res = res_and 
        if emptyAnd:      
            res_or = list(termPList['or'].pop(0))
            while len(termPList['or']) != 0:
                p2 = termPList['or'].pop(0)
                res_or = boolModel.or_ops(res_or, p2)
            res = res_or
        res = boolModel.not_ops(res, termPList['not'])
        
        return res
    
    # TODO: display result with a good ranking algorithm
    def showRankingRes(self, res = [], parsed_query = {'and':[], 'or':[], 'not':[]}):
        if len(res) == 0:
            print(Fore.RED + "No result found" + Style.RESET_ALL)

        # TODO: ranking algorithm here!
        
        # *********** end of ranking algorithm!
        limit = 0
        for item in res:
            limit += 1
            if limit > 5:
                break
            data = raw_data[str(item)]
            print(Fore.YELLOW + "Result {} -> {}".format(limit, data['title']) + Fore.RESET)
            # TODO: show matching words!
            print(Fore.GREEN + data['content'] + Fore.RESET)




# query handler
qa = QueryAnalyzer()
os.system('cls' if os.name == 'nt' else 'clear')
while True:
    inVal = str(input(Fore.BLUE + 'Insert Query:'))
    if inVal.upper() == 'EXIT':
        break
    if inVal == 'clear' or inVal == 'cls':
        os.system('cls' if os.name == 'nt' else 'clear')
        continue
    # TODO: adapt to ranking algorithm
    qa.showRankingRes( 
            qa.search(
                qa.termPListExtractor(
                    qa.queryParser(inVal)
                )
            )
        )

print(Fore.RED + "Query Handler is Shutdown!" + Style.RESET_ALL)
