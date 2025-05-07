import ply.lex as lex

tokens = [
    'PROGRAM', 'VAR', 'BEGIN', 'END', 'IF', 'THEN', 'ELSE', 'FOR', 'WHILE',
    'REPEAT', 'TO', 'DO', 'DOWNTO', 'UNTIL', 'AND', 'OR', 'NOT', 'OF',
    'CASE', 'DIV', 'MOD', 'FUNCTION', 'PROCEDURE', 'WRITELN', 'WRITE', 'READLN', 'READ',
    'BREAK', 'CONTINUE', 'REAL', 'INTEGER', 'BOOLEAN', 'STRING', 'ARRAY',
    'BOOL', 'LENGTH',
    
    'SEMICOLON', 'LPAREN', 'RPAREN', 'DOT', 'COMMA', 'PHRASE', 'ID',
    'COLON', 'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'NUMBER',
    'LESSEQUAL', 'GREATERTHAN', 'GREATEREQUAL', 'DIFFERENT', 'LESSTHAN',
    'EQUALS', 'LBRACKET', 'RBRACKET', 'RANGE'
]

# Expressões Aritméticas
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
t_EQUALS = r'='

# Símbolos
t_SEMICOLON = r';'
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_RANGE = r'\.\.'
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ASSIGN = r':='
t_COLON = r':'

# Palavras reservadas (case insensitive)
def t_PROGRAM(t):
    r'[pP][rR][oO][gG][rR][aA][mM]'
    return t

def t_VAR(t):
    r'[vV][aA][rR]'
    return t    

def t_BEGIN(t):
    r'[bB][eE][gG][iI][nN]'
    return t

def t_END(t):
    r'[eE][nN][dD]'
    return t

def t_IF(t):
    r'[iI][fF]'
    return t

def t_THEN(t):
    r'[tT][hH][eE][nN]'
    return t

def t_ELSE(t):
    r'[eE][lL][sS][eE]'
    return t

def t_FOR(t):
    r'[fF][oO][rR]'
    return t

def t_WHILE(t):
    r'[wW][hH][iI][lL][eE]'
    return t

def t_REPEAT(t):
    r'[rR][eE][pP][eE][aA][tT]'
    return t

def t_TO(t):
    r'[tT][oO]'
    return t

def t_DOWNTO(t):
    r'[dD][oO][wW][nN][tT][oO]'
    return t

def t_DO(t):
    r'[dD][oO]'
    return t

def t_UNTIL(t):
    r'[uU][nN][tT][iI][lL]'
    return t

def t_AND(t):
    r'[aA][nN][dD]'
    return t

def t_OR(t):
    r'[oO][rR]'
    return t

def t_NOT(t):
    r'[nN][oO][tT]'
    return t

def t_OF(t):
    r'[oO][fF]'
    return t

def t_CASE(t):
    r'[cC][aA][sS][eE]'
    return t

def t_DIV(t):
    r'[dD][iI][vV]'
    return t

def t_MOD(t):
    r'[mM][oO][dD]'
    return t

def t_FUNCTION(t):
    r'[fF][uU][nN][cC][tT][iI][oO][nN]'
    return t

def t_PROCEDURE(t):
    r'[pP][rR][oO][cC][eE][dD][uU][rR][eE]'
    return t

def t_WRITELN(t):
    r'[wW][rR][iI][tT][eE][lL][nN]'
    return t

def t_WRITE(t):
    r'[wW][rR][iI][tT][eE]'
    return t

def t_READLN(t):
    r'[rR][eE][aA][dD][lL][nN]'
    return t

def t_READ(t):
    r'[rR][eE][aA][dD]'
    return t

def t_BREAK(t):
    r'[bB][rR][eE][aA][kK]'
    return t

def t_CONTINUE(t):
    r'[cC][oO][nN][tT][iI][nN][uU][eE]'
    return t

def t_REAL(t):
    r'[rR][eE][aA][lL]'
    return t

def t_INTEGER(t):
    r'[iI][nN][tT][eE][gG][eE][rR]'
    return t

def t_BOOLEAN(t):
    r'[bB][oO][oO][lL][eE][aA][nN]'
    return t

def t_STRING(t):
    r'[sS][tT][rR][iI][nN][gG]'
    return t

def t_ARRAY(t):
    r'[aA][rR][rR][aA][yY]'
    return t

def t_LENGTH(t):
    r'[lL][eE][nN][gG][tT][hH]'
    return t

def t_BOOL(t):
    r'[tT][rR][uU][eE]|[fF][aA][lL][sS][eE]'
    t.value = (t.value.lower() == 'true')
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_PHRASE(t):
    r"'[^']*'"
    return t

# Comentários
def t_COMMENT(t):
    r'\{[^}]*\}|\(\*[^*]*\*\)'
    pass  

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

def test_lexer(data):
    lexer.input(data)
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
        tokens_list.append(tok)
    return tokens_list

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            data = file.read()
        test_lexer(data)
    else:
        lex.runmain()
