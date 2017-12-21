import pandas as pd
import json
import time
def row_index(filename):
    with open('row_references/' + filename + '_row_reference') as f:
        json1_str = f.read()
        json1_data = json.loads(json1_str)
        row_references_table = {int(k):int(v) for k,v in json1_data.items()}
    return row_references_table

flist = ['business.csv', 'checkin.csv', 'photos.csv', 'review-1m.csv']
nlist = ['business', 'checkin', 'photos', 'review-1m']
for i in range(len(flist)):
    start = time.time()
    row_reference_tb = row_index(nlist[i])
    table = pd.read_csv(flist[i])
    for c in table.columns:
        g = table.groupby([c])
        sorted_key = sorted(g.groups.iterkeys())
        # Save a hash dict of key to index in memory
        hash_dict = {v:k for k,v in enumerate(sorted_key)}
        # table_index_hash_dict[c] = hash_dict
        with open('index/' + nlist[i] + '_' + c + '_index_hash_dict', 'w') as f:
            json.dump(hash_dict, f)
        # Save a list of row number lists based on sorted_key
        row_numbers = [list(g.groups[k]) for k in sorted_key]
        new_result = []
        for ilist in row_numbers:
            qlist = []
            for element in ilist:
                if element not in row_reference_tb:
                    print "Error locate line number: ", element, " in the row reference file"
                qlist.append(row_reference_tb[element])
            new_result.append(qlist)
        # table_index_row_numbers[c] = row_numbers
        with open('disk/' + nlist[i] + '_' + c + '_index_row_numbers', 'w') as f:
            json.dump(new_result, f)

    end = time.time()
    print 'Index time: %s seconds' % str(end-start)

    # with open('index/' + nlist[i] + '_index_hash_dict', 'w') as f:
    #     json.dump(table_index_hash_dict, f)
    # with open('index/' + nlist[i] + '_index_row_numbers', 'w') as f:
    #     json.dump(table_index_row_numbers, f)
