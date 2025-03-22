import ply.lex as lex

reserved = {
    'program': 'PROGRAM',
    'var': 'VAR',
    'begin': 'BEGIN',
    'end': 'END',
    'writeln': 'WRITELN',
    'readln': 'READLN',
    'for': 'FOR',
    'to': 'TO',
    'do': 'DO',
    'integer': 'INTEGER'
}

tokens = [
    'SEMICOLON', 'LPAREN', 'RPAREN', 'POINT', 'COMMA', 'STRING', 'ID',
    'COLON', 'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'NUMBER'
] + list(reserved.values())

t_SEMICOLON = r';'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_POINT = r'\.'
t_COLON = r':'
t_ASSIGN = r':='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

def t_STRING(t):
    r"'[^']*'"
    t.value = t.value[1:-1] #removes quotes from string
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)  
    return t

def t_COMMENT(t):
    r'\{[^}]*\}'
    pass  

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__':
    lex.runmain()

