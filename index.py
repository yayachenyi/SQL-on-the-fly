import pandas as pd
import json
import time
import io
import csv
def row_to_offset(filename, deliminator, dlength):
    with open(filename,'rb') as content_file:
        content = content_file.read()
    content_file.close()
    li = content.split('\r\n')
    test_files = pd.read_csv(filename)
    test_files.to_csv(filename, line_terminator = '\r\r\n')
    with open(filename,'rb') as content_file:
        content = content_file.read()
    content_file.close()
    li = content.split('\r\r\n')
    fo = open(filename)
    fo.seek(0)
    csv_header = csv.reader(fo)
    linecount = 0
    filelinecount = 0
    # for line in fo:
    #     filelinecount+=1
    # for row in csv_header.next():
    #     if linecount < 10:
    #         print fo.tell()
    #     linecount+=1
    row_to_offset_dict = {}
    start = 0
    print len('\t'), len('\r')
    # ireader = enumerate(csv_header)
    # for i,line in ireader:
    #     row_to_offset_dict[i-1] = start
    #     linesize =
    #     for element in line:
    #         linesize+=len(element)
    #     # if i < 10:
    #     #     print i, line
    #     start += linesize
    #     #row = csv.reader([line]).next()
    #     filelinecount+=1
    print test_files.shape," vs ", linecount, " vs ", filelinecount, " vs ", len(li)

    for i in range(0, len(li)):
        row_to_offset_dict[i-1] = start
        start += (len(li[i])+3)
    with open('row_references/' + filename.replace(".csv","") + '_row_reference', 'w') as f:
        json.dump(row_to_offset_dict, f)
    f.close()
    # fo = open(filename, "r")
    # fo.seek(row_to_offset_dict[165317])
    # csv_header = csv.reader(fo).next()
    # print csv_header
    # csv_header = csv.reader(fo).next()
    # print csv_header
    # fo.seek(row_to_offset_dict[1])
    # csv_header = csv.reader(fo).next()
    # print csv_header
    fo.close()

f1list = ['business.csv', 'checkin.csv']
n1list = ['business', 'checkin']
f2list = ['photos.csv', 'review-1m.csv']
n2list = ['photos', 'review-1m']
flist = ['business.csv', 'checkin.csv', 'photos.csv', 'review-1m.csv']
nlist = ['business', 'checkin', 'photos', 'review-1m']
#flist = ['review-5k.csv', 'review-50k.csv', 'review-500k.csv']
#nlist = ['review-5k', 'review-50k', 'review-500k']
for i in range(len(f1list)):
    row_to_offset(f1list[i],'\n',1)
for i in range(len(f2list)):
    row_to_offset(f2list[i],'\r\n',2)
# for i in range(len(flist)):
#     start = time.time()
#     row_to_offset(flist[i])
#     table = pd.read_csv(flist[i])
#     table_index_hash_dict = {}
#     table_index_row_numbers = {}
#     for c in table.columns:
#         g = table.groupby([c])
#         sorted_key = sorted(g.groups.iterkeys())
#         # Save a hash dict of key to index in memory
#         hash_dict = {v:k for k,v in enumerate(sorted_key)}
#         table_index_hash_dict[c] = hash_dict
#         # Save a list of row number lists based on sorted_key
#         row_numbers = [list(g.groups[k]) for k in sorted_key]
#         table_index_row_numbers[c] = row_numbers
#
#     with open('index/' + nlist[i] + '_index_hash_dict', 'w') as f:
#         json.dump(table_index_hash_dict, f)
#     with open('index/' + nlist[i] + '_index_row_numbers', 'w') as f:
#         json.dump(table_index_row_numbers, f)
#
#     end = time.time()
#     print end - start

# Test on storing index in memory
# start = time.time()
# index = table_index_hash_dict['stars'][5]
# row_numbers = table_index_row_numbers['stars'][index]
# print len(row_numbers)
# end = time.time()
# print end - start
