'''Association Rule Minig'''
'''
    First:
        Find the frequent itemsets, whose support are larger than min_support
            1. Apriori
            2. FP-Growth
    Second:
        Find the strong rules in the within the mining results from process above
'''
## import packages
import pandas as pd
import numpy as np
import math
import time
import sys, getopt
from itertools import combinations
from time import process_time
from Apriori import Apriori
from FP_growth import FPTree

## variable defintions
'''min_support = 0.1   # minimum support 
min_support_upper_bound = 0.5   
min_confidence = 0.1   # minimum confidence
min_confidence_upper_bound = 0.6  '''

## function definitions
def main(argv):   # main function 
    filename = ""   # input file name
    algorithm = ""   # algo. to find the freq. patterns
    min_support = 0.0
    min_confidence = 0.0
    try:
        opts, args = getopt.getopt(argv, "hf:m:s:c:", ["file=", "method=", "minimum support=", "minimum confidence="])
    except getopt.GetoptError:
        print("python association_rule.py -f <inputfile> -m <algorithm> -s <minimum support> -c <minimum confidence>")
        sys.exit(2)   # misuse of the command
    for opt, arg in opts:
        if opt == "-h":   # cpmmand help 
            print("python association_rule.py -f <inputfile> -m <algorithm> -s <minimum support> -c <minimum confidence>")
            sys.exit()
        elif opt in ("-f"):
            filename = arg
        elif opt in ("-m"):
            algorithm = arg
        elif opt in ("-s"):
            min_support = float(arg)
        elif opt in ("-c"):
            min_confidence = float(arg)
    df, tranc_list, tranc_count, unique_items = read_file(filename)   # read data
    start_t = time.perf_counter()
    if algorithm.startswith("a"):   # apriori
        apriori = Apriori(tranc_list, unique_items)   # create Apriori obj
        freq_itemsets = apriori.run(min_sup=min_support)   # run Apriori algorithm and get the frequent patterns
    elif algorithm.startswith("f"):   # fp-growth
        fp_tree = FPTree(tranc_list, len(tranc_list), min_support)   # create FPTree obj
        freq_itemsets = fp_tree.run()   # run FP-growth algorithm and get the frequent patterns
    end_t = time.perf_counter()
    print("Frequent patterns with min_support {}:".format(min_support))
    for freq_item, freq in freq_itemsets.items():
        sup = freq/tranc_count
        print("{}-element frequent itemsets: {}\nSupport: {}".format(len(freq_item), freq_item, freq/tranc_count))
    print("")
    print("Strong rules with min_confidence {}:".format(min_confidence))
    gen_rules(freq_itemsets, min_confidence)   # generate all the qualified rules
    print("\n===========" + algorithm  + " Finds Frequent Itemsets Using===========")
    print("Time:", end_t - start_t)
        
def read_file(filename):   # read input file
    if filename.endswith(".csv"):
        df = pd.read_csv("Dataset1.csv")
        tranc_list = df.drop(["Item(s)"], axis=1).values.tolist()   # trancsaction list
        tranc_list = [[item for item in tranc if item == item] for tranc in tranc_list]   # remove the nan values
        tranc_count = len(tranc_list)   # total number of transactions
        unique_items = pd.Series(df.drop(["Item(s)"], axis=1).values.flatten()).unique().tolist()
        unique_items.remove(np.nan)   # remove the nan element in the unique_items list
    elif filename.endswith(".data"):
        df = pd.read_table("AR.data", delim_whitespace=True, header=None)
        df.drop([1], axis=1, inplace=True)
        df = df.set_index(0, drop=True)
        tranc_list = list()   # init. transaction list as an empty one
        for i in range(1, df.index.max()+1):
            if type(df[2][i].tolist()) == type(int(1)):
                tranc_list.append([(df[2][i]).tolist()])
            else:
                tranc_list.append((df[2][i]).tolist())
        tranc_count = len(tranc_list)   # total number of transactions
        unique_items = df[2].unique()
    return df, tranc_list, tranc_count, unique_items

def gen_rules(freq_itemsets, min_confidence):   # gen all the qualified association rules (s1 -> s2)
    have_strong_rule = False
    for freq_pattern, freq in freq_itemsets.items():
        #if freq / tranc_count < min_support_upper_bound:
        if len(freq_pattern) < 2:   # freq. 1-itemset
            continue
        else:
            u = set(freq_pattern)
            for s1_l in range(1, len(u)):
                s1_list = list(combinations(u, s1_l))   # list all combinations of s1 with length s1_q
                for s1 in s1_list:
                    s1 = tuple(sorted(s1))
                    s2 = u - set(s1)   # complementary set of s1
                    confidence = freq / freq_itemsets[s1]
                    if confidence >= min_confidence:# and confidence < min_confidence_upper_bound:   # qualified as a strong rule
                        have_strong_rule = True
                        print("Rule {} -> {}\nConfidence: {}".format(s1, s2, confidence))
    if not have_strong_rule:
        print("There's no strong rule generated!")
                      
## EDA
# check if there's any duplicated items in one trancsaction
'''for i, tranc in df.iterrows():
    if tranc.dropna().duplicated().any():
        print(i)
'''

## Main
if __name__ == '__main__':
    main(sys.argv[1:])


## Apriori
'''min_support = 0.05
min_confidence = 0.4
df, tranc_list, tranc_count, unique_items = read_file("Dataset1.csv")   # read data
apriori_start_t = time.perf_counter()
apriori = Apriori(tranc_list, unique_items)   # create Apriori obj
freq_itemsets = apriori.run(min_sup=min_support)   # run Apriori algorithm and get the frequent patterns
apriori_end_t = time.perf_counter()
print("Frequent patterns with min_support {}:".format(min_support))
for freq_item, freq in freq_itemsets.items():
    sup = freq/tranc_count
    #if sup < min_support_upper_bound:
    print("{}-element frequent itemsets: {}\nSupport: {}".format(len(freq_item), freq_item, freq/tranc_count))
print("")
print("Strong rules with min_confidence {}:".format(min_confidence))
gen_rules(freq_itemsets)   # generate all the qualified rules
print("\n===========Apriori Finds Frequent Itemsets Using===========")
print("Time:", apriori_end_t - apriori_start_t)
'''

## FP-growth
'''df, tranc_list, tranc_count, unique_items = read_file("AR.data")   # read data
fp_growth_start_t = time.perf_counter()
fp_tree = FPTree(tranc_list, len(tranc_list), min_support)   # create FPTree obj
freq_itemsets = fp_tree.run()   # run FP-growth algorithm and get the frequent patterns
fp_growth_end_t = time.perf_counter()
print("Frequent patterns with min_support {}:".format(min_support))
for freq_item, freq in freq_itemsets.items():
    sup = freq/tranc_count
    #if sup < min_support_upper_bound:
    print("{}-element frequent itemsets: {}\nSupport: {}".format(len(freq_item), freq_item, freq/tranc_count))
print("")
print("Strong rules with min_confidence {}:".format(min_confidence))
gen_rules(freq_itemsets)   # generate all the qualified rules
print("\n===========FP-growth Finds Frequent Itemsets Using===========")
print("Time:", fp_growth_end_t - fp_growth_start_t)'''
