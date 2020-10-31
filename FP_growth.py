'''Tree element definitions for FP-Tree'''
import copy
from itertools import combinations

# class "FPTree" definition
class FPTree:
    def __init__(self, tranc_list, tranc_count, min_sup):   # initializer
        self.root = None   # init. the tree with no node
        self.tranc_list = tranc_list   # transaction list
        self.tranc_count = tranc_count   # transaction sample count 
        self.min_sup = min_sup   # minimum support
        self.freq_items = dict()   # store the mapping relationship of frequent 1-itemsets
        self.freq_pattern_dict = dict()   # record the frequent pattern growing process
        self.freq_itemsets = dict()   # all frequent itemsets with frequency
        self.__find_freq_items()   # find frequent 1-itemsets
        self.__rearrange_tranc_list()   # rearrange the transaction list 
        self.header_table = FPHeaderTable(self.freq_items)   # header table to record each item node (helping prefix pattern tracing), for main FP-Tree only
        for item, freq in self.freq_items.items():
            self.freq_pattern_dict[item] = dict()
            self.freq_itemsets[(item,)] = freq
        
    def run(self):    # run the FP-growth algorithm
        self.__build()   # build the fp_tree
        self.__get_cond_pattern_bases()   # the first call for conditional pattenrn base
        self.__get_cond_fp_trees()   # the first call for conditional fp tree
        self.__get_freq_patterns(self.freq_pattern_dict)   # recursively mine the frequent patterns
        self.__gen_freq_patterns(self.freq_pattern_dict, list())   # generate all the frequent patterns and return
        return self.freq_itemsets
        
    def get_tree(self):   # return the tree root to help operation
        return self.root
    
    def display(self, node):   # display the tree structure
        for child_item, child_node in node.children.items():
            if len(child_node.children) > 0:
                print("{}'s children are {}".format(child_node.item, list(child_node.children.keys())))
                self.display(child_node)
    
    def __build(self):   # build the fp_tree for rearranged transaction list
        self.root = FPNode("root")
        for i, tranc in enumerate(self.tranc_list):
            self.__add_tranc(tranc)
    
    def __find_freq_items(self):   # find the frequent 1-itemsets
        # count freq. for all items
        for tranc in self.tranc_list:
            for item in tranc:
                if item in self.freq_items:
                    self.freq_items[item] += 1
                else:
                    self.freq_items[item] = 1
        
        # filter out the one under minimum support
        freq_items_tracer = dict(self.freq_items)
        for item, freq in freq_items_tracer.items():
            if freq / self.tranc_count < self.min_sup:   # if support count of 1-item is smaller than minimum support  
                del self.freq_items[item]
        
        # reorder the freq items dict based on freq.
        self.freq_items = dict((sorted(self.freq_items.items(), key=lambda item: item[1], reverse=False)))
                
    def __rearrange_tranc_list(self):   # rearrange the transaction list according to frequent items
        freq_items_name = list(self.freq_items.keys())
        tranc_list_rearranged = list()
        for tranc in self.tranc_list:
            new_tranc = list(filter(lambda item: item in freq_items_name, tranc))
            if len(new_tranc) > 0:
                tranc_list_rearranged.append(sorted(new_tranc, key=lambda x: self.freq_items.get(x), reverse=True))
        self.tranc_list = tranc_list_rearranged
         
    def __add_tranc(self, tranc, freq=1):   # add transaction into the FP-Tree
        node = self.root   # init. node as root of the tree    
        for item in tranc:
            if item not in list(node.children.keys()):   
                node.children[item] = FPNode(item, freq)   # add item as child (create a new branch), the init. freq is different for main FP-Tree and conditional one
                node.children[item].parent = node   # assign node's parent when child is created
                self.header_table.add_header(node.children[item])   # add node to the corresponding position in header table (like linked list, "whole milk" -> header1 -> header2...)
            else:
                node.children[item].add_freq(freq)   # add one to frequency to indicate the occurrence of an item
            node = node.children[item]   # go to child to match the next item
    
    def __get_cond_pattern_bases(self):   # get the conditional pattern bases with headers
        self.cond_pattern_bases = dict(self.header_table.table)
        delete_keys = list()   # delete the cond_pattern_base if no prefix_pattern is found
        for item, headers in self.header_table.table.items():
            prefix_patterns = list()
            for header in headers:
                prefix_pattern = self.__get_prefix_pattern(header)   # get the prefix pattern of the header 
                if len(prefix_pattern) != 0:   # header isn't the direct child of root  
                    prefix_patterns.append((prefix_pattern, header.freq))   # add one prefix pattern and path freq
            if len(prefix_patterns) > 0:
                self.cond_pattern_bases[item] = prefix_patterns   # update conditional pattern base for one item
            else:
                delete_keys.append(item)
        for delete_key in delete_keys:
            del self.cond_pattern_bases[delete_key]
            
    def __get_cond_fp_trees(self):   # get the conditional FP-Tree
        self.cond_fp_trees = dict(self.cond_pattern_bases)
        for item, cond_pattern_base in self.cond_pattern_bases.items():   # loop through conditionla pattern base for each item
            tranc_list = self.__extract_virtual_tranc_list_and_freq(cond_pattern_base)
            cond_fp_tree = FPTree(tranc_list, self.tranc_count, self.min_sup)   # create a new conditional FP-Tree
            cond_fp_tree.__build()
            self.cond_fp_trees[item] = cond_fp_tree

    def __get_freq_patterns(self, freq_pattern_dict):   # get all the final frequent patterns
        for item_name, tree in self.cond_fp_trees.items():
            if len(tree.freq_items) != 0:   # if there's conditional fp trees, the freq pattern mining will need to go ahead 
                for item, freq in (tree.freq_items.items()):
                    freq_pattern_dict[item_name][item] = dict()
                    freq_pattern_dict[item_name][str(item) + "freq"] = freq
                tree.__get_cond_pattern_bases()
                tree.__get_cond_fp_trees()
                tree.__get_freq_patterns(freq_pattern_dict[item_name])
            else:
                continue 
    
    def __gen_freq_patterns(self, freq_pattern_dict, pattern):   # generate all the frequent patterns from frequent pattern dict
        for item, sub_dict in freq_pattern_dict.items():
            if type(sub_dict) == type(dict()):
                pattern_extract = copy.deepcopy(pattern)
                pattern_extract.append(item)
                pattern_propagate = copy.deepcopy(pattern_extract)
                if len(pattern_extract) != 1:
                    pattern_extract.append(freq_pattern_dict[str(item)+"freq"])   # append the pattern frequency
                    self.freq_itemsets[tuple(sorted(pattern_extract[:-1]))] = pattern_extract[-1:][0]
                self.__gen_freq_patterns(sub_dict, pattern_propagate)
                
    def __get_prefix_pattern(self, header):   # get the prefix pattern from header (not included) to root 
        prefix_pattern = list()   # single prefix pattern for one item (single path)
        node = header.parent
        while node != self.root:   # while the path tracing doesn't finish
            prefix_pattern.append(node.item)
            node = node.parent
        prefix_pattern.reverse()   # reverse the prefix pattern from top to down
        return prefix_pattern
        
    def __extract_virtual_tranc_list_and_freq(self, cond_pattern_base):   # extract the virtual transaction list (prefix path) and frequency (path frequency) out
        virtual_tranc_list = list()
        for prefix_path_with_freq in cond_pattern_base:
            for path_count in range(prefix_path_with_freq[1]):
                virtual_tranc_list.append(prefix_path_with_freq[0])
        return virtual_tranc_list
    
    def __gen_path(self, path, node):   # generate all the paths from root to leaves
        if len(node.children) > 0:
            for child_item, child_node in node.children.items():
                path.append(child_node)    # append item on the path to path
                self.__gen_path(copy.deepcopy(path), child_node)
        else:
            self.paths.append(path)   # append the path to list storing all the paths
            return 
    
# class "FPNode" definition
class FPNode:
    def __init__(self, item, freq=1):   # initializer
        self.parent = None   # parent node
        self.children = dict()   # store the mapping relationship of children ("item name" -> real item node)
        self.item = item   # item name
        self.freq = freq   # init. as freq when new node is created (different for FP-Tree and conditional one)
        
    def add_freq(self, freq):   # add one to freq 
        self.freq += freq

# class "FPHeaderTable" definition
class FPHeaderTable:
    def __init__(self, freq_1_itemsets):   # initializer
        self.freq_1_itemsets = freq_1_itemsets
        self.table = dict()
        self.__init_table()
    
    def __init_table(self):   # init. the header table
        for item, freq in self.freq_1_itemsets.items():
            self.table[item] = list()   # init. as a list for every item name (header)
        
    def add_header(self, node):   # add a header to the corresponding bucket (like linking all the node with the same item name)
        self.table[node.item].append(node)
        
        
    
    
    
    
    
    
    
    