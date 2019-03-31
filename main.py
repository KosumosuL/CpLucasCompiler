if __name__ == '__main__':
    from LexicalAnalyzer import getLex
    lex_result = getLex('LAGrammer', 'code.cpl')
    if lex_result != 'ERROR':
        from SyntaxParser import getSyn
        syn_result = getSyn('SPGrammer', lex_result)
        print(syn_result)
