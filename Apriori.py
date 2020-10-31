'''Genenerate freqent patterns using Apriori algorithm'''
import pandas as pd
from itertools import combinations

# class "Apriori" definition
class Apriori:
    def __init__(self, tranc_list, unique_items):   # niitializer
        self.freq_itemsets = dict()
        self.tranc_list = tranc_list
        self.tranc_count = len(tranc_list)
        self.unique_items = unique_items
        self.min_sup = 0
        self.C1 = dict()
        for item in self.unique_items:
            self.C1[(item,)] = 0   # candidate 1-itemset initialization
    
    def run(self, min_sup):   # run the algorithm and return the frequent patterns
        self.min_sup = min_sup
        self.__Apriori(self.C1, 2)
        return self.freq_itemsets
    
    def __Apriori(self, C, k):   # apriori algorithm for finding frequent itemsets
        if not bool(C):    # if there aren't any candidate itemsets 
            return
        
        # scan through the transaction and count the itemset's support number
        for itemset, itemset_count in C.items():   # loop throught all the candidate frequent itemsets
            for tranc in self.tranc_list:   # loop through all the trancsaction
                if set(itemset).issubset(set(tranc)):   # itemset is the subset of the transaction, meaning itemset is in transaction    
                    C[itemset] += 1   # add one to the corresponding item
        
        # generate L (frequent) from C (candidate)
        L = dict(C)   # init. fequent k-itemsets with candidate k-itemsets
        under_support = list()   # record the itemset whose supprt is smaller the min_support
        for itemset, itemset_count in C.items():
            if itemset_count / self.tranc_count < self.min_sup:   # if the support is smaller to minimum support
                under_support.append(itemset)    
                del L[itemset]   # remove the specific k-itemset
        if len(L) > 0:
            self.freq_itemsets.update(L)
        
        # generate candidate itemsets for next scanning (**notice**: subset test)
        C_new = self.__permute(L, k)   # premute all possible candidate itemsets
        C_temp = dict(C_new)
        for itemset in C_temp:
            for itemset_under_support in under_support:
                if set(itemset_under_support).issubset(set(itemset)) and C_new[itemset]:
                    del C_new[itemset]   # delete itemset not passing subset test
        
        return self.__Apriori(C_new, k+1)
    
    def __permute(self, Lk_minus_1, k):   # generate all the k-itemsets from (k-1)-itemsets
        Lk_minus_1 = list(Lk_minus_1.keys())   # list of k-1-itemsets
        cand_k_itemsets = dict()    
        for i in range(0, len(Lk_minus_1)-1):
            for j in range(i+1, len(Lk_minus_1)):
                s1 = set(Lk_minus_1[i])
                s2 = set(Lk_minus_1[j])
                if len(s1.intersection(s2)) == k-2:   # check the intersection to meet the qualification
                    new_k_itemset = tuple(sorted(s1.union(s2)))
                    cand_k_itemsets[new_k_itemset] = 0   # init. candidate k-itemsets with 0
        return cand_k_itemsets