import ply.lex as lex

reserved = {
    'program': 'PROGRAM',
    'function': 'FUNCION',
    'procedure': 'PROCEDURE',
    'var': 'VAR',
    'begin': 'BEGIN',
    'end': 'END',
    'writeln': 'WRITELN',
    'readln': 'READLN',
    'for': 'FOR',
    'not': 'NOT',
    'to': 'TO',
    'do': 'DO',
    'repeat': 'REPEAT',
    'until': 'UNTIL',
    'set': 'SET',
    'uses': 'USES',
    'label': 'LABEL',
    'with': 'WITH',
    'shl': 'SHL',
    'shr': 'SHR',
    'downto': 'DOWNTO',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'and': 'AND',
    'div': 'DIV',
    'do': 'DO',
    'mod': 'MOD',
    'of': 'OF',
    'array': 'ARRAY',
    'break': 'BREAK',
    'case': 'CASE',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'or': 'OR',
    'string': 'STRING',
    'type': 'TYPE',
    'xor': 'XOR',
}

tokens = [
    'SEMICOLON', 'LPAREN', 'RPAREN', 'DOT', 'COMMA', 'PHRASE', 'ID',
    'COLON', 'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'NUMBER', 'BOOL',
    'LESSEQUAL', 'GREATERTHAN', 'GREATEREQUAL', 'DIFFERENT', 'LESSTHAN',
    'EQUALS', 'LBRACKET', 'RBRACKET', 'RANGE', 
] + list(reserved.values())

# Expressões Ariméticas
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

# Expressões Relacionais
t_LESSEQUAL = r'<='
t_LESSTHAN = r'<'
t_GREATERTHAN = r'>'
t_GREATEREQUAL = r'>='
t_DIFFERENT = r'<>'
t_ASSIGN = r':='
t_EQUALS = r'='

# Simbolos
t_SEMICOLON = r';'
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_RANGE = r'\.\.'
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r':'

def t_PHRASE(t):
    r"'[^']*'"
    t.value = t.value[1:-1] #removes quotes from string
    return t

def t_BOOL(t):
    r'true|false'
    if t.value == 'true':
        t.value = True
    else:
        t.value = False
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?([eE][+-]?\d+)?'
    if '.' in t.value or 'e' in t.value or 'E' in t.value:
        t.value = float(t.value) 
    else:
        t.value = int(t.value) 
    return t

def t_COMMENT(t):
    r'\{[^}]*\}|\(\*[^*]*\*\)'
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

