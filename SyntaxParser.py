from Definitions import *
import copy

TERMINAL = copy.deepcopy(DTERMINAL)
NONTERMINAL = set()
NULLABLE = set()
PRODUCTION = []
FIRST = {}
ITEMList = []
ACTION = []
GOTO = []

class Item(object):

    def __init__(self, start):
        self.prod = self.get_closure(start)
        self.next = dict()

    def __str__(self):
        return 'prod: ' + str(self.prod) + '\nnext: ' + str(self.next)

    def __eq__(self, other):
        return sorted(self.prod) == sorted(other.prod)

    def get_closure(self, start):
        def get_lookahead(str, la):
            res = set()
            for l in la:
                tmp = copy.deepcopy(str)
                tmp.append('#' if l == '#' and str == [] else l)
                for c in tmp:
                    if c == '#':
                        res.add(c)
                        break
                    elif c in TERMINAL:
                        res |= {c}
                        break
                    elif c in NONTERMINAL:
                        if c not in NULLABLE:
                            res |= FIRST[c]
                            break
                        else:
                            res |= FIRST[c] - {'@'}
            return res

        prod = copy.deepcopy(start)
        queue = copy.deepcopy(start)
        while len(queue):
            # tmpqueue = copy.deepcopy(queue)
            # for lhs, rhs, la in tmpqueue:
            lhs, rhs, la = queue.pop(0)
            pos = rhs.index('.')
            if pos < len(rhs) - 1:
                if rhs[pos + 1] in NONTERMINAL:
                    newla = get_lookahead(([] if pos == len(rhs) - 2 else rhs[pos + 2:]), la)
                    for plhs, prhs in PRODUCTION:
                        if plhs == rhs[pos + 1]:
                            if prhs == ['@']:
                                tmp = ['.']
                            else:
                                tmp = copy.deepcopy(prhs)
                                tmp.insert(0, '.')
                            if [plhs, tmp, newla] not in prod:
                                prod.append([plhs, tmp, newla])
                                queue.append([plhs, tmp, newla])
        # make lookahead gathered
        for i in range(len(prod)):
            for j in range(i + 1, len(prod)):
                if prod[i][:1] == prod[j][:1]:
                    prod[i][2] |= prod[j][2]
        return prod

def preprocess(path):
    def preprocess(code):
        for p in code:
            lhs, rhs = p.split(' -> ')
            lhs, rhs = lhs.strip(), rhs.split(' ')
            NONTERMINAL.add(lhs)
            for idx in range(len(rhs)):
                rh = rhs[idx].strip()
                if rh not in TERMINAL:
                    NONTERMINAL.add(rh)
                rhs[idx] = rh
            PRODUCTION.append([lhs, rhs])
        if '@' in NONTERMINAL:
            NONTERMINAL.remove('@')
        TERMINAL.add('@')
        # print(TERMINAL)
        # print(NONTERMINAL)
        # print(PRODUCTION)

    def getNullable():
        change = True
        while change:
            change = False
            for [lhs, rhs] in PRODUCTION:
                if lhs not in NULLABLE:
                    if rhs == ['@']:
                        NULLABLE.add(lhs)
                        change = True
                    else:
                        nullable = True
                        for c in rhs:
                            nullable &= (c in NULLABLE)
                        if nullable:
                            NULLABLE.add(lhs)
                            change = True
        # print(NULLABLE)

    def getFirst():
        mem = dict()
        for n in NONTERMINAL:
            FIRST[n] = set()
        def recur_get_first(tar):
            if tar in mem:
                return mem[tar]
            for [lhs, rhs] in PRODUCTION:
                if lhs == tar:
                    for c in rhs:
                        if c in TERMINAL:
                            FIRST[lhs].add(c)
                            break
                        elif c in NONTERMINAL:
                            recur_get_first(c)
                            FIRST[lhs] |= FIRST[c]
                            if c not in NULLABLE:
                                FIRST[lhs] -= {'@'}
                                mem[lhs] = copy.deepcopy(FIRST[lhs])
                                break
        for n in NONTERMINAL:
            recur_get_first(n)
        # print(FIRST)

    with open(path, 'r') as f:
        code = f.readlines()
        preprocess(code)
        getNullable()
        getFirst()

def getSynParser(target):
    def LR1Parsing():
        it = Item([['<S>', ['.', '<start>'], {'#'}]])
        ITEMList.append(it)
        queue = [it]
        while len(queue):
            item = queue.pop(0)
            mp = dict()
            for lhs, rhs, la in item.prod:
                pos = rhs.index('.')
                if pos < len(rhs) - 1:
                    if rhs[pos + 1] not in mp.keys():
                        mp[rhs[pos + 1]] = []
                    # 这里不会重复，因此不用set（）
                    import copy
                    tmp = copy.deepcopy(rhs)
                    tmp[pos], tmp[pos+1] = tmp[pos+1], tmp[pos]
                    mp[rhs[pos + 1]].append([lhs, tmp, la])
            # print(mp)
            for key in mp.keys():
                val = mp[key]
                tmp = Item(val)
                if tmp not in ITEMList:
                    ITEMList.append(tmp)
                    queue.append(tmp)
                item.next[key] = ITEMList.index(tmp)

        if DEBUG:
            for idx in range(len(ITEMList)):
                print(idx)
                print(ITEMList[idx])

    def getTable():
        for idx in range(len(ITEMList)):
            ACTION.append({})
            GOTO.append({})
            for t in TERMINAL:
                ACTION[idx][t] = '  '
            for t in NONTERMINAL - {'<S>'}:
                GOTO[idx][t] = ' '

        for idx in range(len(ITEMList)):
            prod = ITEMList[idx].prod
            for lhs, rhs, la in prod:
                if rhs.index('.') == len(rhs)-1:
                    for l in la:
                        if rhs == ['.']:
                            id = PRODUCTION.index([lhs, ['@']])
                        else:
                            id = PRODUCTION.index([lhs, rhs[:-1]])
                        if id == 0:
                            ACTION[idx][l] = 'acc'
                        else:
                            ACTION[idx][l] = 'r' + str(id)
            next = ITEMList[idx].next
            for t in next.keys():
                if t in TERMINAL:
                    ACTION[idx][t] = 'S' + str(next[t])
                else:
                    GOTO[idx][t] = str(next[t])

        # print(ACTION)
        # print(GOTO)

    def analysis(target):
        queue = target
        stateStack, charStack = [0], []
        while True:
            curState = stateStack[-1]
            inputChar = queue[0]
            cur = ACTION[curState][inputChar]
            if cur[0] == 'S':
                queue.pop(0)
                charStack.append(inputChar)
                stateStack.append(int(cur[1:]))
            elif cur[0] == 'r':
                prod = PRODUCTION[int(cur[1:])]
                if prod[1] != ['@']:
                    for i in range(len(prod[1])):
                        charStack.pop()
                        stateStack.pop()
                curState = stateStack[-1]
                cur = GOTO[curState][prod[0]]
                if cur != ' ':
                    charStack.append(prod[0])
                    stateStack.append(int(cur))
            elif inputChar == '#' and cur == 'acc':
                return 'ACCEPT'
            else:
                return 'ERROR'

            if DEBUG:
                print(charStack)
                print(stateStack)

    try:
        LR1Parsing()
        getTable()
        return analysis(target)
    except Exception as e:
        print(e)
        return 'ERROR'

def getSyn(SPG, CODE):
    preprocess(SPG)
    ans = getSynParser(CODE)
    if ans == 'ERROR':
        print('ERROR IN SYNTAX PARSER')
        return ans
    return ans

if __name__ == '__main__':
    from LexicalAnalyzer import getLex
    lex_result = getLex('LAGrammer', 'code.cpl')
    if lex_result != 'ERROR':
        syn_result = getSyn('SPGrammer', lex_result)
        print(syn_result)