import ply.lex as lex

reserved = {
    'program' : 'PROGRAM',
    'var' : 'VAR',
    'begin' : 'BEGIN',
    'end' : 'END',
    'writeln' : 'WRITELN',
}

tokens = [
    'SEMICOLON',
    'LPAREN',
    'RPAREN',
    'POINT',
    'STRING',
    'ID',
] + list(reserved.values())

t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_POINT = r'\.'

def t_STRING(t):
    r"'[^']*'"
    t.value = t.value[1:-1] #removes quotes from the string
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character'%s" % t.value[0])
    t.lexer.skip(1)

t_ignore = (' \t')

lexer = lex.lex()

if __name__ == '__main__':
    lex.runmain()
