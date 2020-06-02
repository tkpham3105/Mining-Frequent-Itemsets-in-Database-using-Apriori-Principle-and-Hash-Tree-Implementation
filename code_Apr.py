# -*- coding: utf-8 -*-
"""
APRIORI_ALGORITHM
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
# Generate frequent itemsets of length 1 from the data 
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
    #  
    return counts_filtered


###############################################################################
# Perform pruning process based on the unqualified itemsets
# Return a list of satisfied candidates after pruning
def perform_pruning(prev_candidates, new_candidates, length_prune):
    candidates_after_prune = []

    for candidate in new_candidates:
        # get all length-"length_prune" subsets of each candidate
        # check whether they are in the previous list of frequent itemsets or not
        all_subsets = list(itertools.combinations(set(candidate), length_prune))
        
        found = True
        for itemset in all_subsets:
            itemset = tuple(sorted(itemset))
            if itemset not in list(prev_candidates): 
                found = False # if not found, then do not consider the candidate
                break
        if found == True:
            candidates_after_prune.append(candidate)
    return candidates_after_prune

            
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
        
        # Take candidates of length "length" only
        if len(new_candidates[i]) != length:
            drops.append(i)
      
    # Get the list of qualitfied candidates and avoid duplications
    new_candidates_final = [value for i, value in enumerate(new_candidates) if i not in drops]

    new_candidates_final = set(tuple(sorted(candidate)) for candidate in new_candidates_final)
    return list(new_candidates_final)


###############################################################################
# Perform apriori algorithm to mine frequent itemsets
def apriori(data, minsup):    
    transactions = data.readlines()
    #transactions = transactions[:20000]
    for i, transaction in enumerate(transactions):
        transactions[i] = transaction.split(" ")
        transactions[i].remove("\n") # Note to remove "\n" character
        transactions[i] = set(map(int, transactions[i])) 
   
    layers = [] # n-th layer store all the frequent itemsets of a length n 
    
    # Perform first_generate to get frequent itemsets and pruning_set of infrequent itemsets of length 1
    start = time.time()
    candidates = first_generate(transactions, minsup)
    
    # Append first layer
    layers.append(candidates)
    
    prev_candidates = candidates.keys() 
    length = 2

    while True: 
        # Generate candidates of desired length
        new_candidates = generate_candidates(prev_candidates, length)
        
        # Perform pruning process before scanning through database
        if length > 2:

            new_candidates = perform_pruning(prev_candidates, new_candidates, length-1)    
        new_counts = {}

        # Counting frequency of desired-length itemsets
        for transaction in transactions:
            for candidate in new_candidates:
                candi = set(candidate)
                inter = candi.intersection(transaction) # count frequency by checking intersection with every elements (transactions) in database
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
            
    return layers, time.time() - start # return results of frequent itemsets and runtime

   
###############################################################################
# Run the algorithm
result = apriori(data, 400)


###############################################################################
# Write results to file, uncomment if wanted
f = open("frequent_itemsets_apr.txt", "w")
for items in result[0]:
    for key, val in items.items():
        f.write(str(key) + "\t" + str(val) + "\n")

f.write("Time\t : \t" + str(result[1]))
f.close()


###############################################################################
