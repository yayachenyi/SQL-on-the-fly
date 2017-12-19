def nothandler(notcodition):
    if ' NOT ' in notcodition:
        if " >= " in notcodition:
            notcodition = notcodition.replace(" >= "," < ").replace(' not ','')
            conds = notcodition.split(" < ")
            op = '<'
        elif " <= " in notcodition:
            notcodition = notcodition.replace(" <= "," > ").replace(' not ','')
            conds = notcodition.split(" > ")
            op = '>'
        elif " <> " in notcodition:
            notcodition = notcodition.replace(" <> "," == ").replace(' not ','')
            conds = notcodition.split(" == ")
            op = '=='
        elif " = " in notcodition:
            notcodition = notcodition.replace(" = "," != ").replace(' not ','')
            conds = notcodition.split(" != ")
            op = '!='
        elif " < " in notcodition:
            notcodition = notcodition.replace(" < "," >= ").replace(' not ','')
            conds = notcodition.split(" >= ")
            op = '>='
        elif " > " in notcodition:
            notcodition = notcodition.replace(" > "," <= ").replace(' not ','')
            conds = notcodition.split(" <= ")
            op = '<='
        else:
            print "Cannot perform NOT operation"
    else:
        if " >= " in notcodition:
            conds = notcodition.split(" >= ")
            op = '>='
        elif " <= " in notcodition:
            conds = notcodition.split(" <= ")
            op = '<='
        elif " <> " in notcodition:
            notcodition = notcodition.replace(" <> "," != ")
            conds = notcodition.split(" != ")
            op = '!='
        elif " = " in notcodition:
            notcodition = notcodition.replace(" = "," == ")
            conds = notcodition.split(" == ")
            op = '=='
        elif " < " in notcodition:
            conds = notcodition.split(" < ")
            op = '<'
        elif " > " in notcodition:
            conds = notcodition.split(" > ")
            op = '>'
        elif " LIKE " in notcodition:
            var = notcodition.split(" LIKE ")
            conds = var
            if ('%' in var[1]) or ('_' in var[1]):
                var[1] = var[1].replace('%', '.*')
                var[1] = var[1].replace('_', '.')
                var[1] = "'^" + var[1][1:-1] + "$'"
                notcodition = var[0] + ".str.match(" + var[1] +") == True"
                op = 'LIKE'
            else:
                notcodition = notcodition.replace('LIKE', '==')
                var[1] = var[1][1:-1]
                op = '=='
    return notcodition, conds, op

def condsplit(condstr):
    ret = []
    if ' OR ' in condstr:
        ret = condstr.split(' OR ')
        conjunct = 'OR'
    else:
        assert False, 'Wrong conjuction word'
    return ret, conjunct


class Condition:
    def __init__(self, condstr):
        notcodition, conds, op = nothandler(condstr)
        self.str = notcodition
        self.left = conds[0]
        self.right = conds[1]
        self.op = op
        if '__' in self.right:
            self.type = 'M' # Multi-table
        elif (' + ' in self.right) or (' - ' in self.right) or (' * ' in self.right) or (' / ' in self.right):
            self.type = 'A' # Arithmatic
        else:
            self.type = 'S' # Single-table

class CompCondition:
    def __init__(self, condstr):
        conditions, conjunct = condsplit(condstr)
        self.conjuct = conjunct
        self.conditions = [Condition(c) for c in conditions]
        self.type = 'C' # Compound
