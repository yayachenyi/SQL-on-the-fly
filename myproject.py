import pandas as pd
pd.options.mode.chained_assignment = None
import json
import sqlparse
import itertools
import ast
import bisect
import csv
import copy
import sys, time, re
from multiprocessing import Pool
from condition import Condition, CompCondition

def index(segments, tables):
    key = segments[1]
    with open('index/' + key + '_index_hash_dict', 'r') as f:
        hash_dict = json.load(f)
    with open('index/' + key + '_index_row_numbers', 'r') as f:
        row_numbers = json.load(f)
    tables[key] = (hash_dict, row_numbers)

def row_index(segments, row_references):
    key = segments[1]
    with open('row_references/' + key + '_row_reference') as f:
        json1_str = f.read()
        json1_data = json.loads(json1_str)
        row_references_table = {int(k):int(v) for k,v in json1_data.items()}
    row_references[key+".csv"] = row_references_table

def drop(segments, tables):
    key = segments[1]
    tables.pop(key)

def parse(line):
    return sqlparse.parse(line)[0]

def generalhandler(command):
    parsedcommand = sqlparse.format(command, reindent=True)
    parsedlist = parsedcommand.split("\n")
    i = 0
    selectcommand = ''
    while "FROM" not in parsedlist[i]:
        selectcommand+=parsedlist[i]
        i+=1
    fromcommand = ''
    while i<len(parsedlist) and ("WHERE" not in parsedlist[i]):
        fromcommand+=parsedlist[i]
        i+=1
    wherecommand=''
    for i in range(i,len(parsedlist)):
        wherecommand+=parsedlist[i]
        i+=1
    commands = {}
    commands["SELECT"] = selectcommand.split("SELECT ")[1]
    commands["FROM"] = fromcommand.split("FROM ")[1]
    if wherecommand == '':
        commands["WHERE"] = ''
    else:
        commands["WHERE"] = wherecommand.split("WHERE ")[1]
    return commands

def fromParser(command):
    abb2table = {}
    table_init = []
    query = re.split(r'\s*,\s*', command)
    if len(query) > 1:
        for q in query:
            tbs = re.split(r'\s+', q)
            abb2table[tbs[-1]] = tbs[0]
    else:
        tbs = re.split(r'\s+', query[0])
        assert len(tbs) == 1, 'No abbreviations for single table'
        abb2table[tbs[0]] = tbs[0]
    table_num = len(query)
    print abb2table
    return abb2table, table_num

def condsplit(condition):
    ret = []
    if ' OR ' in condition:
        ret = condition.split(' OR ')
    else:
        assert False, 'Wrong conjuction word'
    return ret

def whereParser(command):
    ret = []
    if command == '':
        return ret
    conds = re.split(r'\s*AND\s*', command)
    for c in conds:
        if c[0] == '(' and c[-1] == ')':
            ret.append(CompCondition(c[1:-1]))
        else:
            ret.append(Condition(c))
    return ret

def getRowNumbersSingleTable(tables, table, cond):
    key = cond.right
    attr = cond.left
    keyl = tables[table][0][attr]
    if cond.op != 'LIKE':
        key = cond.right
        attr = cond.left
        if key in keyl:
            idx = keyl[key]
            if cond.op == '==':
                row_numbers = tables[table][1][attr][idx]
            elif cond.op == '!=':
                temp = tables[table][1][attr][:idx] + tables[table][1][attr][idx+1:]
                row_numbers = [item for sublist in temp for item in sublist]
            elif cond.op == '>=':
                temp = tables[table][1][attr][idx:]
                row_numbers = [item for sublist in temp for item in sublist]
            elif cond.op == '<=':
                temp = tables[table][1][attr][:idx+1]
                row_numbers = [item for sublist in temp for item in sublist]
            elif cond.op == '>':
                temp = tables[table][1][attr][idx+1:]
                row_numbers = [item for sublist in temp for item in sublist]
            elif cond.op == '<':
                temp = tables[table][1][attr][:idx]
                row_numbers = [item for sublist in temp for item in sublist]
        else:
            idx = bisect.bisect(keyl.keys(), key)
            if cond.op == '==':
                row_numbers = []
            elif cond.op == '!=':
                row_numbers = -1
            elif cond.op == '>=':
                temp = tables[table][1][attr][idx:]
                row_numbers = [item for sublist in temp for item in sublist]
            elif cond.op == '<=':
                temp = tables[table][1][attr][:idx]
                row_numbers = [item for sublist in temp for item in sublist]
            elif cond.op == '>':
                temp = tables[table][1][attr][idx:]
                row_numbers = [item for sublist in temp for item in sublist]
            elif cond.op == '<':
                temp = tables[table][1][attr][:idx]
                row_numbers = [item for sublist in temp for item in sublist]
    else:
        row_numbers = []
        for k in keyl:
            if re.match(cond.right[2:-2], k):
                idx = keyl[k]
                row_numbers += tables[table][1][attr][idx]
    return set(row_numbers)

def getTable(table, row_numbers, test_files, row_references):
    # Given a table name and a row_numbers list, return a pandas datafram.
    print table, "Table name"
    start = time.time()
    fo = open(table, "r")
    fo.seek(0)
    csv_header = csv.reader(fo).next()
    pd_li = []
    for keyoffest in row_numbers:
        #print keyoffest,row_references[table][keyoffest]
        fo.seek(row_references[table][keyoffest])
        pd_li.append(csv.reader(fo).next())
    fo.close()
    end = time.time()
    print 'Time: %s seconds' % str(end-start)
    #print pd_li
    pdframe = pd.DataFrame(pd_li, columns = csv_header)
    end = time.time()
    print 'Time: %s seconds' % str(end-start)
    return pdframe
    #return test_files[table].loc[row_numbers,]

def singleTableJoin(tables, row_references, abb2table, whereConds, test_files):
    table = abb2table.keys()[0]
    if whereConds == []:
        table_init = pd.read_csv(table+'.csv')
        return table_init, whereConds
    row_numbers = -1
    idx = 0
    for cond in whereConds:
        if cond.type != 'S':
            break
        else:
            idx += 1
            if row_numbers == -1:
                row_numbers = getRowNumbersSingleTable(tables, table, cond)
            else:
                row_numbers = row_numbers & getRowNumbersSingleTable(tables, table, cond)
    if row_numbers == -1:
        table_init = pd.read_csv(table+'.csv')
    else:
        table_init = getTable(table+'.csv', list(row_numbers), test_files, row_references)
    return table_init, whereConds[idx:]

def multiTableJoin(tables, row_references, table_num, abb2table, whereConds, test_files):
    row_numbers = {(abb2table[k]+k):-1 for k in abb2table}
    print row_numbers,"rwonumbers"
    idx = 0
    for cond in whereConds:
        if cond.type != 'S':
            break
        else:
            idx += 1
            table_index = abb2table[cond.left.split('__')[0]]+cond.left.split('__')[0]
            table = abb2table[cond.left.split('__')[0]]
            cond.left = cond.left.split('__')[1]
            if row_numbers[table_index] == -1:
                row_numbers[table_index] = getRowNumbersSingleTable(tables, table, cond)
            else:
                row_numbers[table_index] = row_numbers[table_index] & getRowNumbersSingleTable(tables, table, cond)

    for t in abb2table:
        table = abb2table[t]
        table_index = (abb2table[t]+t)
        print table_index," table_index"
        if row_numbers[table_index] != -1:
            row_numbers[table_index] = getTable(table+'.csv', list(row_numbers[table_index]), test_files, row_references)
            print "not wrong yet"
            row_numbers[table_index].columns = [t+'__'+i for i in row_numbers[table_index].columns]
            print "wrong"

    for cidx in range(idx, idx+table_num-1):
        print whereConds[cidx],cidx
        cond = whereConds[cidx]
        table1 = abb2table[cond.left.split('__')[0]]
        table2 = abb2table[cond.right.split('__')[0]]
        table1_index = (abb2table[cond.left.split('__')[0]]+cond.left.split('__')[0])
        table2_index = (abb2table[cond.right.split('__')[0]]+cond.right.split('__')[0])
        attr1 = cond.left.split('__')[1]
        attr2 = cond.right.split('__')[1]
        keys1 = tables[table1][0][attr1].keys()
        keys2 = tables[table2][0][attr2].keys()
        keys  = set(keys1) & set(keys2)

        if type(row_numbers[table1_index]) != int:
            keys = set(list(row_numbers[table1_index][cond.left])) & keys
            if type(row_numbers[table2_index]) != int:
                keys = set(list(row_numbers[table2_index][cond.right])) & keys
                data1 = row_numbers[table1_index][row_numbers[table1_index][cond.left].isin(list(keys))]
                data2 = row_numbers[table2_index][row_numbers[table2_index][cond.right].isin(list(keys))]
                data1['merge_key'] = data1[cond.left]
                data2['merge_key'] = data2[cond.right]
                data = pd.merge(data1, data2, on = 'merge_key')
                row_numbers[table1_index] = data
                row_numbers[table2_index] = data
            else:
                idx_list = [tables[table2][0][attr2][i] for i in keys]
                row_numbers[table2_index] = [tables[table2][1][attr2][j] for j in idx_list]
                row_numbers[table2_index] = [r for sublist in row_numbers[table2_index] for r in sublist]
                row_numbers[table2_index] = getTable(table2+'.csv', list(row_numbers[table2_index]), test_files, row_references)
                row_numbers[table2_index].columns = [cond.right.split('__')[0]+'__'+i for i in row_numbers[table2_index].columns]
                data1 = row_numbers[table1_index][row_numbers[table1_index][cond.left].isin(list(keys))]
                data2 = row_numbers[table2_index][row_numbers[table2_index][cond.right].isin(list(keys))]
                data1['merge_key'] = data1[cond.left]
                data2['merge_key'] = data2[cond.right]
                data = pd.merge(data1, data2, on = 'merge_key')
                row_numbers[table1_index] = data
                row_numbers[table2_index] = data
        else:
            if type(row_numbers[table2_index]) != int:
                keys = set(list(row_numbers[table2_index][cond.right])) & keys
                idx_list = [tables[table1][0][attr1][i] for i in keys]
                row_numbers[table1_index] = [tables[table1][1][attr1][j] for j in idx_list]
                row_numbers[table1_index] = [r for sublist in row_numbers[table1_index] for r in sublist]
                row_numbers[table1_index] = getTable(table1+'.csv', list(row_numbers[table1_index]), test_files, row_references)
                row_numbers[table1_index].columns = [cond.left.split('__')[0]+'__'+i for i in row_numbers[table1_index].columns]
                data1 = row_numbers[table1_index][row_numbers[table1_index][cond.left].isin(list(keys))]
                data2 = row_numbers[table2_index][row_numbers[table2_index][cond.right].isin(list(keys))]
                data1['merge_key'] = data1[cond.left]
                data2['merge_key'] = data2[cond.right]
                data = pd.merge(data1, data2, on = 'merge_key')
                row_numbers[table1_index] = data
                row_numbers[table2_index] = data
            else:
                idx_list = [tables[table1][0][attr1][i] for i in keys]
                row_numbers[table1_index] = [tables[table1][1][attr1][j] for j in idx_list]
                row_numbers[table1_index] = [r for sublist in row_numbers[table1_index] for r in sublist]
                row_numbers[table1_index] = getTable(table1+'.csv', list(row_numbers[table1_index]), test_files, row_references)
                row_numbers[table1_index].columns = [cond.left.split('__')[0]+'__'+i for i in row_numbers[table1_index].columns]
                idx_list = [tables[table2][0][attr2][i] for i in keys]
                row_numbers[table2_index] = [tables[table2][1][attr2][j] for j in idx_list]
                row_numbers[table2_index] = [r for sublist in row_numbers[table2_index] for r in sublist]
                row_numbers[table2_index] = getTable(table2+'.csv', list(row_numbers[table2_index]), test_files, row_references)
                row_numbers[table2_index].columns = [cond.right.split('__')[0]+'__'+i for i in row_numbers[table2_index].columns]
                data1 = row_numbers[table1_index][row_numbers[table1_index][cond.left].isin(list(keys))]
                data2 = row_numbers[table2_index][row_numbers[table2_index][cond.right].isin(list(keys))]
                data1['merge_key'] = data1[cond.left]
                data2['merge_key'] = data2[cond.right]
                data = pd.merge(data1, data2, on = 'merge_key')
                row_numbers[table1_index] = data
                row_numbers[table2_index] = data
    return data.drop('merge_key', 1), whereConds[cidx+1:]

def tableFilter(table, leftConds):
    T = table
    metaconds = []
    for cond in leftConds:
        if cond.type == 'C':
            temp = []
            for c in cond.conditions:
                if c.type == 'M':
                    temp.append('(T.' + c.left + c.op + 'T.' + c.right + ')')
                else:
                    temp.append('(T.' + c.left + c.op + c.right + ')')
            metaconds.append('(' + ' | '.join(temp) + ')')
        elif cond.type == 'M':
            metaconds.append('(T.' + cond.left + cond.op + 'T.' + cond.right + ')')
        else:
            metaconds.append('(T.' + cond.left + cond.op + cond.right + ')')
    metacond = ' & '.join(metaconds)
    return table[eval(metacond)]

def selectParser(table, command):
    if command == '*':
        return table
    else:
        query = re.split(r'\s*,\s*', command)
        if re.split(r'\s+', query[0])[0] == 'DISTINCT':
            query[0] = re.split(r'\s+', query[0])[1]
            if query[0] == '*':
                return table.drop_duplicates()
            else:
                return table[query].drop_duplicates()
        else:
            return table[query]


def main():
    files = ['review-1m.csv', 'photos.csv', 'checkin.csv', 'business.csv']
    test_files = {}
    # for f in files:
    #     test_files[f] = pd.read_csv(f)
    # print 'Test files loaded successfully'

    tables = {}
    row_references = {}
    while True:
        line = sys.stdin.readline().strip('\n')

        start = time.time()

        if line == 'exit':
            return False

        if line == '':
            continue

        segments = line.split(' ')
        if segments[0]== 'USE':
            # Table indexing
            index(segments, tables)
            row_index(segments, row_references)
            print 'Index loaded successfully!'
        elif segments[0] == 'DROP':
            # Table dropping
            drop(segments, tables)
            print 'Index dropped successfully!'
        else:
            commands = generalhandler(line)
            abb2table, table_num = fromParser(commands['FROM'])
            whereConds = whereParser(commands['WHERE'])
            if table_num == 1:
                table_init, leftConds = singleTableJoin(tables, row_references, abb2table, whereConds, test_files)
            else:
                table_init, leftConds = multiTableJoin(tables, row_references, table_num, abb2table, whereConds, test_files)
            if leftConds == []:
                table_filter = table_init
            else:
                table_filter = tableFilter(table_init, leftConds)
            table_select = selectParser(table_filter, commands['SELECT'])
            # table_select = table_select.reset_index(drop=True)
            print table_select
            end = time.time()
            print 'Time: %s seconds' % str(end-start)


if __name__ == "__main__":
    main()
