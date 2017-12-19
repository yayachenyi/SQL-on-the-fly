import pandas as pd
import json
import time

# flist = ['business.csv', 'checkin.csv', 'photos.csv', 'review-1m.csv']
# nlist = ['business', 'checkin', 'photos', 'review-1m']
flist = ['review-5k.csv', 'review-50k.csv', 'review-500k.csv']
nlist = ['review-5k', 'review-50k', 'review-500k']
for i in range(len(flist)):
    start = time.time()

    table = pd.read_csv(flist[i])
    table_index_hash_dict = {}
    table_index_row_numbers = {}
    for c in table.columns:
        g = table.groupby([c])
        sorted_key = sorted(g.groups.iterkeys())
        # Save a hash dict of key to index in memory
        hash_dict = {v:k for k,v in enumerate(sorted_key)}
        table_index_hash_dict[c] = hash_dict
        # Save a list of row number lists based on sorted_key
        row_numbers = [list(g.groups[k]) for k in sorted_key]
        table_index_row_numbers[c] = row_numbers

    with open('index/' + nlist[i] + '_index_hash_dict', 'w') as f:
        json.dump(table_index_hash_dict, f)
    with open('index/' + nlist[i] + '_index_row_numbers', 'w') as f:
        json.dump(table_index_row_numbers, f)

    end = time.time()
    print end - start

# Test on storing index in memory
# start = time.time()
# index = table_index_hash_dict['stars'][5]
# row_numbers = table_index_row_numbers['stars'][index]
# print len(row_numbers)
# end = time.time()
# print end - start
