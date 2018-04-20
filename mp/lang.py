from copy import copy
import functools
import sys

from ply import lex, yacc

from ast import *

reserved = {
    'while': 'WHILE',
    'print': 'PRINT',
    'and': 'OP_AND',
    'or': 'OP_OR',
    'not': 'OP_NOT',
}

tokens = [
    'TRUE', 'FALSE',
    'FLOAT', 'INTEGER',
    'NAME', 'STRING',
    'NEWLINE',
    'OP_FLOOR_DIV', 'OP_EQ', 'OP_NEQ', 'OP_GTEQ', 'OP_LTEQ', 'OP_UNARY_NEG'
] + list(reserved.values())

literals = [
    '=', '[', ']', ',', ';', '(', ')',
    '+', '-', '*', '/', '%', '^', '>', '<', '!'
]

precedence = (
    ('right', 'OP_NOT', 'OP_UNARY_NEG'),
    ('left',  'OP_AND', 'OP_OR'),
    ('left',  'OP_EQ', 'OP_NEQ'),
    ('left', '>', '<', 'OP_GTEQ', 'OP_LTEQ'),
    ('left', '+', '-'),
    ('left', '*', '/', 'OP_FLOOR_DIV', '%'),
    ('right', '^'),
)

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

t_OP_FLOOR_DIV = '//'
t_OP_EQ = '=='
t_OP_NEQ = '!='
t_OP_GTEQ = '>='
t_OP_LTEQ = '<='
t_OP_UNARY_NEG = '-'

def t_TRUE(t):
    r'True'
    t.value = True
    return t

def t_FALSE(t):
    r'False'
    t.value = False
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

t_ignore = ' \t'

def t_error(t):
    print_error(
        "Parse error",
        "Unrecognized character: %s" % t.value[0],
        t.lineno,
        t.lexpos
    )
    t.lexer.skip(1)

lexer = lex.lex()

def inject_production(f):
    @functools.wraps(f)
    def wrapper(p):
        f(p)
        if p[0] is not None and isinstance(p[0], Node):
            p[0].p = copy(p)

    wrapper.co_firstlineno = f.__code__.co_firstlineno
    return wrapper

@inject_production
def p_main(p):
    """main : statement_list"""
    p[1].execute()

@inject_production
def p_statement_list(p):
    """statement_list : statement ";"
                      | statement_list statement ";" """
    if len(p) > 3:
        p[1].add_child(p[2])
        p[0] = p[1]
    else:
        p[0] = StatementList()
        p[0].add_child(p[1])

@inject_production
def p_statement_print(p):
    'statement : PRINT expression'
    p[0] = Print(expr=p[2])

@inject_production
def p_statement_assign(p):
    'statement : NAME "=" expression'
    p[0] = Assign(name=p[1], expr=p[3])

@inject_production
def p_expression_index(p):
    'expression : expression "[" expression "]"'
    p[0] = Index(target=p[1], index=p[3])

@inject_production
def p_expression_atom(p):
    '''expression : atom
                  | "[" atom_list "]"'''
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = p[1]

@inject_production
def p_expression_arithmetic(p):
    '''expression : expression "+" expression
                  | expression "-" expression
                  | expression "/" expression
                  | expression OP_FLOOR_DIV expression
                  | expression "*" expression
                  | expression "%" expression
                  | expression "^" expression
    '''
    p[0] = ArithmeticOp(left=p[1], right=p[3], op=p[2])

@inject_production
def p_expression_comparison(p):
    '''expression : expression OP_EQ expression
                  | expression OP_NEQ expression
                  | expression OP_GTEQ expression
                  | expression OP_LTEQ expression
                  | expression ">" expression
                  | expression "<" expression
    '''
    p[0] = ComparisonOp(left=p[1], right=p[3], op=p[2])

@inject_production
def p_expression_logical(p):
    '''expression : expression OP_AND expression
                  | expression OP_OR expression
    '''
    p[0] = LogicalOp(left=p[1], right=p[3], op=p[2])

@inject_production
def p_expression_unary(p):
    '''expression : OP_NOT expression
                  | OP_UNARY_NEG expression
    '''
    p[0] = UnaryOp(expr=p[2], op=p[1])

def p_expression_group(p):
    'expression : "(" expression ")"'
    p[0] = p[2]

@inject_production
def p_atom_list(p):
    '''atom_list : atom
                 | atom_list ',' atom'''
    if len(p) > 2:
        p[1].items.append(p[3])
        p[0] = p[1]
    else:
        p[0] = List(items=[p[1]])

@inject_production
def p_atom_name(p):
    'atom : NAME'
    p[0] = Lookup(name=p[1])

@inject_production
def p_atom_number(p):
    '''atom : FLOAT
            | INTEGER
            | STRING
            | TRUE
            | FALSE'''
    p[0] = Literal(value=p[1])


def p_error(p):
    if p:
        raise SyntaxError(token=p)
    else:
        print_error(
            "Syntax error",
            "Unexpected end of file",
            source.count('\n'),
            len(source) - 1
        )

def find_column(input, lexpos):
    line_start = input.rfind('\n', 0, lexpos) + 1
    return (lexpos - line_start) + 1


def print_error(error, message, line_number, pos):
    lines = source.split('\n')
    print "%s at line %d: %s" % (error, line_number, message)
    print " %s" % lines[line_number - 1]
    print " %s^" % (" " * find_column(source, pos - 1))


yacc.yacc()
source = '''
a = False;
b = True;
print a and b;
c = not a and b;
print c;
'''

try:
    yacc.parse(source, tracking=True)
except LexicalError as error:
    print_error("Lexical error", error.message, error.line_number, error.pos)
except SyntaxError as error:
    print_error("Syntax error", error.message, error.line_number, error.pos)
except ParseError as error:
    print_error("Parse error", error.message, error.line_number, error.pos)
except RuntimeError as error:
    print_error("Runtime error", error.message, error.line_number, error.pos)
