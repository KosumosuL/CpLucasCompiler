from Definitions import *

def preprocess(path):
    def preprocess(grammer):
        NFA = []
        N, T, F, S, Z = set(), set(), dict(), set(), set('$')
        flag = True

        for p in grammer:
            if p == '###\n' or p == '###':
                NFA.append([N, T, F, S, Z])
                N, T, F, S, Z = set(), set(), dict(), set(), set('$')
                flag = True
                continue

            lhs, rhs = p.split('->')
            lhs, rhs = lhs.strip(), rhs.strip()
            if rhs == '\\n':
                rhs = '\n'
            N.add(lhs)
            if flag:
                S.add(lhs)
                flag = False

            if lhs not in F:
                F[lhs] = dict()

            # solve digit
            pos = rhs.find('<digit>')
            if pos != -1:
                for idx in range(10):
                    idx = str(idx)
                    if idx not in F[lhs]:
                        F[lhs][idx] = set()
                    F[lhs][idx].add(rhs[7:])
                    N.add(rhs[7:])
                    T.add(idx)
                continue
            # solve symbol1
            pos = rhs.find('<symbol1>')
            if pos != -1:
                for idx in range(len(symbol1)):
                    idx = symbol1[idx]
                    if idx not in F[lhs]:
                        F[lhs][idx] = set()
                    F[lhs][idx].add(rhs[9:])
                    N.add(rhs[9:])
                    T.add(idx)
                continue
            # solve symbol2
            pos = rhs.find('<symbol2>')
            if pos != -1:
                for idx in range(len(symbol2)):
                    idx = symbol2[idx]
                    if idx not in F[lhs]:
                        F[lhs][idx] = set()
                    F[lhs][idx].add(rhs[9:])
                    N.add(rhs[9:])
                    T.add(idx)
                continue
            # solve symbol3
            pos = rhs.find('<symbol3>')
            if pos != -1:
                for idx in range(len(symbol3)):
                    idx = symbol3[idx]
                    if idx not in F[lhs]:
                        F[lhs][idx] = set()
                    F[lhs][idx].add(rhs[9:])
                    N.add(rhs[9:])
                    T.add(idx)
                continue
            # solve letter
            pos = rhs.find('<letter>')
            if pos != -1:
                for idx in range(26):
                    if chr(idx + 65) not in F[lhs]:
                        F[lhs][chr(idx + 65)] = set()
                    F[lhs][chr(idx + 65)].add(rhs[8:])
                    if chr(idx + 97) not in F[lhs]:
                        F[lhs][chr(idx + 97)] = set()
                    F[lhs][chr(idx + 97)].add(rhs[8:])
                    N.add(rhs[8:])
                    T.add(chr(idx + 65))
                    T.add(chr(idx + 97))
                continue
            # solve trivial situation
            lpos, rpos = rhs.rfind('<'), rhs.rfind('>')
            if lpos != -1 and rpos != -1:
                if rhs[:lpos] not in F[lhs]:
                    F[lhs][rhs[:lpos]] = set()
                F[lhs][rhs[:lpos]].add(rhs[lpos:])
                N.add(rhs[lpos:])
                T.add(rhs[:lpos])
            else:
                if rhs not in F[lhs]:
                    F[lhs][rhs] = set()
                F[lhs][rhs].add('$')  # '$' is final state
                if rhs != '@':  # '@' is eps state
                    T.add(rhs)

        # print(NFA)
        return NFA

    def ep_closure(src, f):
        import copy
        ans = copy.deepcopy(src)
        queue = list(ans)
        while len(queue):
            s = queue.pop(0)
            if s in f and '@' in f[s]:
                for tar in f[s]['@']:
                    if tar not in ans:
                        queue.append(tar)
                        ans.add(tar)
        return ans

    def move(src, f, ed):
        tar = set()
        for s in src:
            if s in f:
                if ed in f[s]:
                    tar |= f[s][ed]
        return tar

    def nfa2dfa(N, T, F, S, Z):
        DN, DT, DF, DS, DZ = [], T, dict(), set(), set()
        queue = []

        t = ep_closure(S, F)
        DN.append(t)
        queue.append(t)
        while len(queue):
            p = queue.pop(0)
            if DN.index(p) not in DF:   # 正规文法转换的NFA终态一定无出边
                DF[DN.index(p)] = dict()
            for a in T:
                tnext = ep_closure(move(p, F, a), F)
                if len(tnext) == 0:
                    continue
                if tnext not in DN:
                    DN.append(tnext)
                    queue.append(tnext)
                DF[DN.index(p)][a] = DN.index(tnext)

        for p in DN:
            for s in S:
                if s in p:
                    DS.add(DN.index(p))
            for z in Z:
                if z in p:
                    DZ.add(DN.index(p))
        return [DN, DT, DF, DS, DZ]

    def process(NFA):
        DFA = []
        for N, T, F, S, Z in NFA:
            DFA.append(nfa2dfa(N, sorted(T), F, S, Z))
        return DFA

    with open(path, 'r') as f:
        NFA = preprocess(f.readlines())
        # print(NFA)
        DFA = process(NFA)
        # print(DFA)
        return DFA

def getLexAnalysis(path, DFA):
    code = ''

    def getchar():
        global curPos
        curPos += 1
        if curPos == len(code):
            return 'END'
        return code[curPos]

    def scan():
        global curPos
        curChar = getchar()
        while curChar.isspace():
            curChar = getchar()

        if curChar == 'END':
            return 'END'

        finalStr, finalType, finalPos = '', 'undefine', curPos
        tmpPos = curPos
        for dfa in DFA:
            curPos = tmpPos - 1
            curChar = getchar()
            N, T, F, S, Z = dfa
            # DFA 初态唯一
            s = list(S)[0]

            curType = N[s]
            curState = s
            curStr = ''
            while curChar in F[curState]:
                curStr += curChar
                curState = F[curState][curChar]
                curChar = getchar()

            if curState in Z:
                if len(curStr) > len(finalStr):
                    finalStr, finalType, finalPos = curStr, curType, curPos

        if finalType == 'undefine':
            return 'ERROR'
        else:
            curPos = finalPos - 1
            return [finalStr, finalType]

    try:
        with open(path, 'r') as f:
            code = f.read()
            code += '\n'
            res = []
            while True:
                ans = scan()
                if DEBUG:
                    print(ans)
                if ans == 'END':
                    break
                elif ans == 'ERROR':
                    return ans
                else:
                    res.append(ans)
        return res
    except Exception as e:
        print(e)
        return 'ERROR'

def postprocess(code):
    ans = []
    for data, type in code:
        if type == {'<limiter>'} or type == {'<keyword>'}:
            ans.append(data)
        elif data == '=':
            ans.append(data)
        else:
            ans.extend(list(type))
    ans.append('#')
    return ans

def getLex(LAG, CODE):
    global curPos
    curPos = -1
    DFA = preprocess(LAG)
    ans = getLexAnalysis(CODE, DFA)
    if ans == 'ERROR':
        print('ERROR IN LEXICAL ANALYSIS')
        return ans
    ans = postprocess(ans)
    return ans

if __name__ == '__main__':
    DFA = preprocess('LAGrammer')
    ans = getLexAnalysis('code.cpl', DFA)
    if ans == 'ERROR':
        print('ERROR IN LEXICAL ANALYSIS')
    else:
        ans = postprocess(ans)
        print(ans)