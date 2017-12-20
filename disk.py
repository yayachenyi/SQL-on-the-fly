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
    row_to_offset_dict = {}
    start = 0

    for i in range(0, len(li)):
        row_to_offset_dict[i-1] = start
        start += (len(li[i])+3)
    with open('row_references/' + filename.replace(".csv","") + '_row_reference', 'w') as f:
        json.dump(row_to_offset_dict, f)
    f.close()
    fo.close()

f1list = ['business.csv', 'checkin.csv']
n1list = ['business', 'checkin']
f2list = ['photos.csv', 'review-1m.csv']
n2list = ['photos', 'review-1m']
for i in range(len(f1list)):
    row_to_offset(f1list[i],'\n',1)
for i in range(len(f2list)):
    row_to_offset(f2list[i],'\r\n',2)
