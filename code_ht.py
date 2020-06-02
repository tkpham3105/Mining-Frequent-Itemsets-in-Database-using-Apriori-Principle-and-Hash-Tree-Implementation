# -*- coding: utf-8 -*-
"""
HASHTREE
@author: PHAM Trung Kien

"""
###############################################################################
# Import needed libraries
import os
import time
import itertools


###############################################################################
# Change the working directory to where the fle a1dataset.txt is located
os.chdir("D:\\tkpham\\COMP4331\\Assignment_1")
#os.chdir("/home/gmo/Downloads/tkpham/Study/COMP4331/")


###############################################################################
# Read the data file  
data = open("a1dataset.txt")


###############################################################################
# Class of Hash Tree's Nodes
class Node: 
    
    # Each node contains a dictionary of children, 
    # status of is leaf or not, 
    # bucket dictionary    
    def __init__(self):
        self.children = {}
        self.isLeaf = True
        self.bucket = {}


###############################################################################
# Class of Hash Tree 
class Tree:
    
    # Each tree contains a root Node, 
    # max_leaf_size represents the max number of elements can be contained in a bucket
    # max_children stands for max number of children node (use in hash function)
    # a list to store frequent itemsets
    def __init__(self, max_leaf_size, max_children):
        self.root = Node()
        self.max_leaf_size = max_leaf_size
        self.max_children = max_children
        self.frequent_itemsets = {}
        
            
    # Hash function to distribute itemsets into the tree
    def hash_f(self, value):
        return int(value) % self.max_children
    
     
    # Recursive function to rescursively insert itemset in order to build up the tree      
    def insert_recur(self, itemset, node, index, count):
        if index == len(itemset):
            if itemset in node.bucket: 
                node.bucket[itemset] += count
            else:
                node.bucket[itemset] = count 
            return
        
        if node.isLeaf: # when the node is a leaf
            if itemset in node.bucket:
                node.bucket[itemset] += count
            else:
                node.bucket[itemset] = count
                
            if len(node.bucket) == self.max_leaf_size:  # if the bucket reach its max, split the node
                for prev_itemset, prev_count in node.bucket.items():
                    key = self.hash_f(prev_itemset[index])
                    if key not in node.children:
                        node.children[key] = Node()
                    
                    self.insert_recur(prev_itemset, node.children[key], index + 1, prev_count) # recursively perform insertion
                
                del node.bucket # delete the bucket after split
                node.isLeaf = False # change the status after split from a leaf to an intermediate node
        else: # when the node is an intermediate node
            key = self.hash_f(itemset[index])
            if key not in node.children:
                node.children[key] = Node()
            self.insert_recur(itemset, node.children[key], index + 1, count) # recursively perform insertion
     
    def insert(self, itemset):
        self.insert_recur(itemset, self.root, 0, 0)
      
    # To traverse the Tree and find the bucket in which this itemset is present
    # If found, increment the support
    def increment_freq(self, itemset):
        track_node = self.root 
        index = 0
        while True:
            if track_node.isLeaf:
                if itemset in list(track_node.bucket):
                    track_node.bucket[itemset] += 1
                break
            key = self.hash_f(itemset[index])
            if key in track_node.children:
                track_node = track_node.children[key]
            else:
                break
            index += 1

    # To traverse the Tree to obtain the frequent itemsets
    def update_dict_freq_itemsets(self, node, minsup):     
        if node.isLeaf:
            for itemset, count in node.bucket.items():
                if count >= minsup:
                    self.frequent_itemsets[itemset] = count
        for child in node.children.values():
            self.update_dict_freq_itemsets(child, minsup)
        

###############################################################################    
# This function is to build the tree based on a list of candidates
def build_tree(list_candidates, max_leaf_size, max_children):
    tree = Tree(max_leaf_size, max_children) # tree created 
    for i, itemset in enumerate(list_candidates):
        print("Inserting itemset num---------------------------------" + str(i+1))
        tree.insert(itemset) # insert itemset into tree
    return tree


###############################################################################    
# Generate frequent itemsets of length 1 and infrequent itemsets of length 1 from the data 
# Return a dictionary with counts respectively for each item 
def first_generate(transactions, minsup):
    counts = {}
    for transaction in transactions:
        for item in transaction: # Loop for counting frequency
            try:
                counts[item] += 1
            except:
                counts[item] = 1
    
    # Filter by minsup 
    counts_filtered = {key: value for key, value in counts.items() if value >= minsup} 
    return counts_filtered


###############################################################################    
# Generate list of all length-"length" subsets from database
def generate_subsets(itemset, length):
    subsets = []
    if len(itemset) >= length:
        itemset = set(itemset)
        subsets = list(itertools.combinations(itemset,length))
        for i in range(len(subsets)):   
            subsets[i] = tuple(sorted(subsets[i]))
    return subsets

###############################################################################
# Generate candidates for frequent itemsets of length 'length' from the previous list of frequent itemsets
# Return the list of "length"-length candidates
def generate_candidates(prev_freq_set, length):
    combination = [(x, y) for x in prev_freq_set for y in prev_freq_set]
    new_candidates = [] # this list is used to store 
    drops = [] # drop-list is used to store the index of unqualified candidates to be remove
    
    # Convert all the possible combinations get from above into tuple of items
    for candidate in combination:
        new = []
        for element in candidate:
            if isinstance(element, tuple):
                for item in element:
                    new.append(item)
            else:
                new.append(element)
        new_candidates.append(tuple(new))  
    
    # Get indices of the unqualified candidates      
    for i, candidate in enumerate(new_candidates):
        new_candidates[i] = tuple(set(candidate))
        
        # Take candidates of length "length" only, append others to drops-list
        if len(new_candidates[i]) != length:
            drops.append(i)       
    # Get the list of qualified candidates and avoid duplications
    new_candidates_final = [value for i, value in enumerate(new_candidates) if i not in drops]
    new_candidates_final = set(tuple(sorted(candidate)) for candidate in new_candidates_final)
    return list(new_candidates_final)


###############################################################################
# Perform pruning process based on the previous list of frequent itemsets
# Return a list of satisfied candidates after pruning
def perform_pruning(prev_candidates, new_candidates, length_prune):
    candidates_after_prune = []
    for i, candidate in enumerate(new_candidates):
        # get all length-"length_prune" subsets of each candidate
        # check whether they are in the previous list of frequent itemsets or not
        all_subsets = list(itertools.combinations(set(candidate), length_prune))
        found = True
        for itemset in all_subsets:
            itemset = tuple(sorted(itemset))
            if itemset not in list(prev_candidates):
                found = False 
                break # if one subset is not found, then do not append to the final list of candidates
        if found == True:
            candidates_after_prune.append(candidate)
    return candidates_after_prune


###############################################################################
# Perform Apriori Algorithm with Hash Tree
def apriori(data, minsup):    
    transactions = data.readlines()
    #transactions = transactions[:30000]
    for i, transaction in enumerate(transactions):
        transactions[i] = transaction.split(" ")
        transactions[i].remove("\n") # Note to remove "\n" character
        transactions[i] = set(sorted(map(int, transactions[i]))) 

    layers = [] # n-th layer store all the frequent itemsets of a length n
    start = time.time()
    # Perform first_generate to get frequent itemsets and pruning_set of infrequent itemsets of length 1
    candidates = first_generate(transactions, minsup)
    
    # Append first layer
    layers.append(candidates)
    
    prev_candidates = candidates.keys() 
    length = 2
    
    while True:
        # Generate candidates of desired length
        new_candidates = generate_candidates(prev_candidates, length)
        MAX_CHILDREN = []
        for candi in new_candidates:
            MAX_CHILDREN.append(list(candi)[length-1])

        # Perform pruning process before scanning through database
        if length > 2:
            new_candidates = perform_pruning(prev_candidates, new_candidates, length-1)
        if len(new_candidates) == 0: # if no candidate can survive after pruning, break the loop and terminate the program 
            break

        if len(new_candidates) > 5: # if after pruning, number of candidates obtained is large enough, then use hash tree to mine frequent itemsets
            MAX_LEAF_SIZE = int(len(new_candidates)) # set value for max_leaf_size
            MAX_CHILDREN = max(MAX_CHILDREN) # set value for max_children
            # Build a hash tree from new_candidates
            tree = build_tree(new_candidates, MAX_LEAF_SIZE, MAX_CHILDREN)

            # Count frequency for each node in the tree
            for i, transaction in enumerate(transactions):
                subsets = generate_subsets(transaction, length)
                if len(subsets) > 0:
                    for subset in subsets:
                        tree.increment_freq(subset)
                print("Done----------Transaction----------" + str(i+1))
        
            # Update to retrieve frequent_itemsets from the tree 
            tree.update_dict_freq_itemsets(tree.root, minsup)
            new_counts_tree = tree.frequent_itemsets
            if not bool(new_counts_tree): # if new_counts is empty
                break
            else:
                layers.append(new_counts_tree)   
                length += 1
                prev_candidates = new_counts_tree.keys()
        #else:
        #    break


        # When number of candidates is too small, it is tedious to use hash tree to consider whether they are frequent itemsets or not.
        # For hashtree, we generate all subsets of desired length of every transactions and perform incrementing for the nodes of 
        # the tree by searching for those subsets in the tree.
        # The above process for such a large dataset is more time-consuming than finding the intersection of each candidate
        # with the all transactions when we do not have many candidates. 
        # If just want to test the hash tree, comment lines from 273->295, change "5" in line 240 to "0" and finally uncomment lines 263 and 264  
        else:
            new_counts = {}
            for transaction in transactions:
                for candidate in new_candidates:
                    candi = set(candidate)
                    inter = candi.intersection(transaction) # count frequency by checking intersection with every transactions in database
                    if len(inter) == length:
                        try:    
                            new_counts[candidate] += 1
                        except:
                            new_counts[candidate] = 1
            if new_counts == {}:
                break # for terminating the program when all candidates do not appear in the database

            else:
                length += 1 # update length for mining higher-length frequent itemsets in the next loop
            
                new_counts_filtered = {key: value for key, value in new_counts.items() if value >= minsup} # get the satisfied new-length frequent itemsets
            
                # Update data for the next iterations
                prev_candidates = new_counts_filtered.keys()
            
                layers.append(new_counts_filtered) # append results

    return layers, time.time()-start


###############################################################################
# Execute the program and store the results
result = apriori(data, 400)
f = open("frequent_itemsets_ht.txt", "w")
for items in result[0]:
    for key, val in items.items():
        f.write(str(key) + "\t" + str(val) + "\n")

f.write("Time\t : \t" + str(result[1]))
f.close()
