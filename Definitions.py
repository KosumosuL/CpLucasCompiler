curPos = -1
symbol1 = [' ', '#', '+', '-', '*', '/', '%', '&', '|', '!', '^', '<', '>', '=', '(', ')', '[', ']', '{', '}', ',', ';', '_', '.', "'"]
symbol2 = [' ', '#', '+', '-', '*', '/', '%', '&', '|', '!', '^', '<', '>', '=', '(', ')', '[', ']', '{', '}', ',', ';', '_', '.', '"']
symbol3 = [' ', '#', '+', '-', '*', '/', '%', '&', '|', '!', '^', '<', '>', '=', '(', ')', '[', ']', '{', '}', ',', ';', '_', '.', '"', "'", '\\']

LIMITER = {')', '}', ',', ']', ';', '(', '[', '{'}
KEYWORD = {'main', 'return', 'for', 'while', 'do', 'continue', 'if', 'else', 'break'}
TYPE = {'<identifier>', '<binary_operator>', '<unary_operator>', '<type>', '<const>', '<constnumber>', '<constliteral>', '<comment>'}
DTERMINAL = {'#'} | LIMITER | KEYWORD | {'='} | TYPE

DEBUG = True