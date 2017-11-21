import pandas as pd
import sqlparse
import sys, time, re

def index(segments, tables):
    key = segments[1].split('/')[-1][:-4]
    df = pd.read_csv(segments[1])
    df.columns = df.columns.str.lower()
    tables[key] = df

def drop(segments, tables):
    key = segments[1].split('/')[-1][:-4]
    tables.pop(key)

def parse(line):
    return sqlparse.parse(line)[0]

def generalhandler(command):
    parsedcommand = sqlparse.format(command, reindent=True)
    parsedlist = parsedcommand.split("\n")
    i = 0
    selectcommand = ''
    while "from" not in parsedlist[i]:
        selectcommand+=parsedlist[i]
        i+=1
    fromcommand = ''
    while i<len(parsedlist) and ("where" not in parsedlist[i]):
        fromcommand+=parsedlist[i]
        i+=1
    wherecommand=''
    for i in range(i,len(parsedlist)):
        wherecommand+=parsedlist[i]
        i+=1
    commands = {}
    commands['select'] = selectcommand.split('select ')[1]
    commands['from'] = fromcommand.split('from ')[1]
    if wherecommand == '':
        commands['where'] = ''
    else:
        commands['where'] = wherecommand.split('where ')[1]
    return commands

def fromParser(tables, command):
    query = command.split(' on ')
    if len(query) > 1:
        tbs = re.split(r',\s+', query[0])
        cds = re.split(r'and\s+', query[1])
        assert len(tbs)>1, 'Please input at least two tables with ON condition'
        dfs = {}
        for t in tbs:
            dfs[t.split(' ')[1]] = tables[t.split(' ')[0]].copy()
            dfs[t.split(' ')[1]].columns = [t.split(' ')[1]+'__'+i for i in dfs[t.split(' ')[1]].columns]
        temp = re.split(r'\s+=\s+', cds[0])
        dfs[temp[0].split('__')[0]]['merge_key'] = dfs[temp[0].split('__')[0]][temp[0]]
        dfs[temp[1].split('__')[0]]['merge_key'] = dfs[temp[1].split('__')[0]][temp[1]]
        ret = pd.merge(dfs[temp[0].split('__')[0]], dfs[temp[1].split('__')[0]], on = 'merge_key')
        if len(cds) > 1:
            for idx in range(1, len(cds)):
                temp = re.split(r'\s+=\s+', cds[idx])
                ret['merge_key'] = ret[temp[0]]
                dfs[temp[1].split('__')[0]]['merge_key'] = dfs[temp[1].split('__')[0]][temp[1]]
                ret = pd.merge(ret, dfs[temp[1].split('__')[0]], on = 'merge_key')
        return ret.drop('merge_key', 1)
    else:
        query = re.split(r',\s+', command)
        assert len(query)==1, 'Please input: ON table1.key=table2.key'
        return tables[command]

def nothandler(notcodition):
    if ' not ' in notcodition:
        if " >= " in notcodition:
            notcodition = notcodition.replace(" >= "," < ").replace(' not ','')
        elif " <= " in notcodition:
            notcodition = notcodition.replace(" <= "," > ").replace(' not ','')
        elif " <> " in notcodition:
            notcodition = notcodition.replace(" <> "," == ").replace(' not ','')
        elif " = " in notcodition:
            notcodition = notcodition.replace(" = "," != ").replace(' not ','')
        elif " < " in notcodition:
            notcodition = notcodition.replace(" < "," >= ").replace(' not ','')
        elif " > " in notcodition:
            notcodition = notcodition.replace(" > "," <= ").replace(' not ','')
        else:
            print "Cannot perform NOT operation"
    else:
        if (" <= " not in notcodition) and (" >= " not in notcodition) and (" = " in notcodition):
            notcodition = notcodition.replace(" = "," == ")
        elif " <> " in notcodition:
            notcodition = notcodition.replace(" <> "," != ")
        elif " like " in notcodition:
            var = notcodition.split(" like ")
            var[1] = var[1].replace('%', '.*')
            var[1] = var[1].replace('_', '.')
            var[1] = "'^" + var[1][1:-1] + "$'"
            notcodition = var[0] + ".str.lower().str.match(" + var[1] +") == True"
    return notcodition

def commandParser(command):
    res = []
    chunkcommand = command.split(" or ")
    for i in range(0,len(chunkcommand)):
        temp = []
        raw = chunkcommand[i].split(" and ")
        for smallchunck in raw:
            temp.append(nothandler(smallchunck))
        res.append(temp)
    return res

def whereParser(table, command):
    if command[0][0] == '':
        return table
    T = table
    ors = []
    megacommand = ""
    for ans in command:
        ans_T = []
        for i in ans:
            segs = i.rstrip().split(' ')
            assert len(segs)>2, 'WHERE condition: cond1 op cond2'
            if segs[0][0] == "(":
                segs[0] = '((T.'+segs[0].replace("(","")
            else:
                segs[0] = '(T.'+segs[0]
            if segs[2] in T.columns:
                segs[2] = 'T.'+segs[2]
            ans_T.append(' '.join(segs) + ')')
        var =  ' & '.join(ans_T)
        if megacommand == "":
            megacommand+=var
        else:
            megacommand+= ("| " + var)
    varr = "((m__imdb_score < 7) | (m__imdb_score >= 7)) & (a__ceremony > 1)"
    return T.query(megacommand.replace("T.",""))

def selectParser(table, command):
    if command == '*':
        return table
    else:
        query = re.split(r',\s+', command)
        return table[query]


def main():
    tables = {}
    while True:
        line = sys.stdin.readline().strip('\n').lower()

        start = time.time()

        if line == 'exit':
            return False

        if line == '':
            continue

        segments = line.split(' ')
        if segments[0]== 'use':
            # Table indexing
            index(segments, tables)
        elif segments[0] == 'drop':
            # Table dropping
            drop(segments, tables)
        else:
            # Query parsing and table querying
            commands = generalhandler(line)
            table_init = fromParser(tables, commands['from'])
            command_parsed = commandParser(commands['where'])
            table_filter = whereParser(table_init, command_parsed)
            table_select = selectParser(table_filter, commands['select'])
            table_select = table_select.reset_index(drop=True)
            print table_select
            # print table_select.to_csv(index=False, header=False)
            end = time.time()
            print 'Time: %s seconds' % str(end-start)


if __name__ == "__main__":
    main()
