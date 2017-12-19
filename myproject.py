import pandas as pd
pd.options.mode.chained_assignment = None
import json
import sqlparse
import itertools
import ast
import bisect
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

def getTable(table, row_numbers, test_files):
    # Given a table name and a row_numbers list, return a pandas datafram.
    return test_files[table].loc[row_numbers,]

def singleTableJoin(tables, abb2table, whereConds, test_files):
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
        table_init = getTable(table+'.csv', list(row_numbers), test_files)
    return table_init, whereConds[idx:]

def multiTableJoin(tables, table_num, abb2table, whereConds, test_files):
    row_numbers = {k:-1 for k in abb2table.values()}
    idx = 0
    for cond in whereConds:
        if cond.type != 'S':
            break
        else:
            idx += 1
            table = abb2table[cond.left.split('__')[0]]
            cond.left = cond.left.split('__')[1]
            if row_numbers[table] == -1:
                row_numbers[table] = getRowNumbersSingleTable(tables, table, cond)
            else:
                row_numbers[table] = row_numbers[table] & getRowNumbersSingleTable(tables, table, cond)

    for t in abb2table:
        table = abb2table[t]
        if row_numbers[table] != -1:
            row_numbers[table] = getTable(table+'.csv', list(row_numbers[table]), test_files)
            row_numbers[table].columns = [t+'__'+i for i in row_numbers[table].columns]

    for cidx in range(idx, idx+table_num-1):
        cond = whereConds[cidx]
        table1 = abb2table[cond.left.split('__')[0]]
        table2 = abb2table[cond.right.split('__')[0]]
        attr1 = cond.left.split('__')[1]
        attr2 = cond.right.split('__')[1]
        keys1 = tables[table1][0][attr1].keys()
        keys2 = tables[table2][0][attr2].keys()
        keys  = set(keys1) & set(keys2)

        if type(row_numbers[table1]) != int:
            keys = set(list(row_numbers[table1][cond.left])) & keys
            if type(row_numbers[table2]) != int:
                keys = set(list(row_numbers[table2][cond.right])) & keys
                data1 = row_numbers[table1][row_numbers[table1][cond.left].isin(list(keys))]
                data2 = row_numbers[table2][row_numbers[table2][cond.right].isin(list(keys))]
                data1['merge_key'] = data1[cond.left]
                data2['merge_key'] = data2[cond.right]
                data = pd.merge(data1, data2, on = 'merge_key')
                row_numbers[table1] = data
                row_numbers[table2] = data
            else:
                idx_list = [tables[table2][0][attr2][i] for i in keys]
                row_numbers[table2] = [tables[table2][1][attr2][j] for j in idx_list]
                row_numbers[table2] = [r for sublist in row_numbers[table2] for r in sublist]
                row_numbers[table2] = getTable(table2+'.csv', list(row_numbers[table2]), test_files)
                row_numbers[table2].columns = [cond.right.split('__')[0]+'__'+i for i in row_numbers[table2].columns]
                data1 = row_numbers[table1][row_numbers[table1][cond.left].isin(list(keys))]
                data2 = row_numbers[table2][row_numbers[table2][cond.right].isin(list(keys))]
                data1['merge_key'] = data1[cond.left]
                data2['merge_key'] = data2[cond.right]
                data = pd.merge(data1, data2, on = 'merge_key')
                row_numbers[table1] = data
                row_numbers[table2] = data
        else:
            if type(row_numbers[table2]) != int:
                keys = set(list(row_numbers[table2][cond.right])) & keys
                idx_list = [tables[table1][0][attr1][i] for i in keys]
                row_numbers[table1] = [tables[table1][1][attr1][j] for j in idx_list]
                row_numbers[table1] = [r for sublist in row_numbers[table1] for r in sublist]
                row_numbers[table1] = getTable(table1+'.csv', list(row_numbers[table1]), test_files)
                row_numbers[table1].columns = [cond.left.split('__')[0]+'__'+i for i in row_numbers[table1].columns]
                data1 = row_numbers[table1][row_numbers[table1][cond.left].isin(list(keys))]
                data2 = row_numbers[table2][row_numbers[table2][cond.right].isin(list(keys))]
                data1['merge_key'] = data1[cond.left]
                data2['merge_key'] = data2[cond.right]
                data = pd.merge(data1, data2, on = 'merge_key')
                row_numbers[table1] = data
                row_numbers[table2] = data
            else:
                idx_list = [tables[table1][0][attr1][i] for i in keys]
                row_numbers[table1] = [tables[table1][1][attr1][j] for j in idx_list]
                row_numbers[table1] = [r for sublist in row_numbers[table1] for r in sublist]
                row_numbers[table1] = getTable(table1+'.csv', list(row_numbers[table1]), test_files)
                row_numbers[table1].columns = [cond.left.split('__')[0]+'__'+i for i in row_numbers[table1].columns]
                idx_list = [tables[table2][0][attr2][i] for i in keys]
                row_numbers[table2] = [tables[table2][1][attr2][j] for j in idx_list]
                row_numbers[table2] = [r for sublist in row_numbers[table2] for r in sublist]
                row_numbers[table2] = getTable(table2+'.csv', list(row_numbers[table2]), test_files)
                row_numbers[table2].columns = [cond.right.split('__')[0]+'__'+i for i in row_numbers[table2].columns]
                data1 = row_numbers[table1][row_numbers[table1][cond.left].isin(list(keys))]
                data2 = row_numbers[table2][row_numbers[table2][cond.right].isin(list(keys))]
                data1['merge_key'] = data1[cond.left]
                data2['merge_key'] = data2[cond.right]
                data = pd.merge(data1, data2, on = 'merge_key')
                row_numbers[table1] = data
                row_numbers[table2] = data
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
    for f in files:
        test_files[f] = pd.read_csv(f)
    print 'Test files loaded successfully'

    tables = {}
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
                table_init, leftConds = singleTableJoin(tables, abb2table, whereConds, test_files)
            else:
                table_init, leftConds = multiTableJoin(tables, table_num, abb2table, whereConds, test_files)
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
