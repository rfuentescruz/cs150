import sys

from ply import lex, yacc

from ast import *

RESERVED = {
    'while': 'WHILE'
}

tokens = [
    'FLOAT', 'INTEGER', 'NAME', 'PRINT', 'STRING'
] + list(RESERVED.values())

literals = ['=', '[', ']', ',', ';']

source = ''

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'(?x)(?<!\\)".*?(?<!\\)"'
    t.value = t.value[1:-1].decode("string-escape")
    return t


def t_PRINT(t):
    r'print '
    return t

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

t_ignore = ' \t\n'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])


lex.lex()

def p_main(p):
    """main : statement_list"""
    p[1].execute()


def p_statement_list(p):
    """statement_list : statement ";"
                      | statement_list statement ";" """
    if len(p) > 3:
        p[1].add_child(p[2])
        p[0] = p[1]
    else:
        p[0] = StatementList(line=p.lineno(1), children=[p[1]])


def p_statement_print(p):
    'statement : PRINT expression'
    p[0] = Print(expr=p[2])


def p_statement_assign(p):
    'statement : NAME "=" expression'
    p[0] = Assign(name=p[1], expr=p[3], line=p.lineno)


def p_expression_index(p):
    'expression : expression "[" expression "]"'
    p[0] = Index(target=p[1], index=p[3], line=p.lineno)


def p_expression_atom(p):
    '''expression : atom
                  | "[" atom_list "]"'''
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_atom_list(p):
    '''atom_list : atom
                 | atom_list ',' atom'''
    if len(p) > 2:
        p[1].items.append(p[3])
        p[0] = p[1]
    else:
        p[0] = List(items=[p[1]], line=p.lineno)


def p_atom_name(p):
    'atom : NAME'
    p[0] = Lookup(name=p[1])


def p_atom_number(p):
    '''atom : FLOAT
            | INTEGER
            | STRING'''
    p[0] = Literal(value=p[1], line=p.lineno)


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


yacc.yacc()
source = '''

a = 1;
b = 1.0;
c = [1, 2, 3, "abc", b];

print [1,2,3,4][1];

'''

try:
    yacc.parse(source, tracking=True)
except LexicalError, e:
    print e
    raise
