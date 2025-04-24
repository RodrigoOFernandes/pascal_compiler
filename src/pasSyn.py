import sys
from pasAnalex import *
from ply import yacc

start = 'program'

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'DIV', 'MOD'),
    ('left', 'EQUALS', 'DIFFERENT', 'LESSEQUAL', 'LESSTHAN', 'GREATERTHAN', 'GREATEREQUAL'),
    ('left', 'OR', 'AND'),
)

def p_program(t):
    'program : header SEMICOLON block DOT'
    pass

def p_header(t):
    'header : PROGRAM ID'
    pass

def p_block(t):
    """block : variable_declaration_part procedure_or_function statement_part"""
    pass

def p_variable_declaration_part(t):
    """variable_declaration_part : VAR variable_declaration_list
                                  | """
    pass

def p_variable_declaration_list(t):
    """variable_declaration_list : variable_declaration variable_declaration_list
                                  | variable_declaration"""
    pass

def p_variable_declaration(t):
    """variable_declaration : id_list COLON type SEMICOLON"""
    pass

def p_id_list(t):
    """id_list : ID
               | ID COMMA id_list"""
    pass

def p_procedure_or_function(t):
    """procedure_or_function : proc_or_func_declaration SEMICOLON procedure_or_function
                              | """
    pass

def p_proc_or_func_declaration(t):
    """proc_or_func_declaration : procedure_declaration
                                 | function_declaration"""
    pass

def p_procedure_declaration(t):
    """procedure_declaration : procedure_heading SEMICOLON block"""
    pass

def p_procedure_heading(t):
    """procedure_heading : PROCEDURE ID
                          | PROCEDURE ID LPAREN parameter_list RPAREN"""
    pass

def p_function_declaration(t):
    """function_declaration : function_heading SEMICOLON block"""
    pass

def p_function_heading(t):
    """function_heading : FUNCTION type
                         | FUNCTION ID COLON type
                         | FUNCTION ID LPAREN parameter_list RPAREN COLON type"""
    pass

def p_parameter_list(t):
    """parameter_list : parameter COMMA parameter_list
                       | parameter"""
    pass

def p_parameter(t):
    """parameter : ID COLON type"""
    pass

def p_type(t):
    """type : REAL
            | INTEGER
            | BOOLEAN
            | STRING
            | array_type"""
    pass

def p_array_type(t):
    """array_type : ARRAY LBRACKET range RBRACKET OF type"""
    pass

def p_range(t):
    """range : expression RANGE expression"""
    pass

def p_statement_part(t):
    """statement_part : BEGIN statement_sequence END"""
    pass

def p_statement_sequence(t):
    """statement_sequence : statement SEMICOLON statement_sequence
                           | statement"""
    pass

def p_statement(t):
    """statement : assignment_statement
                 | statement_part
                 | if_statement
                 | while_statement
                 | repeat_statement
                 | for_statement
                 | procedure_or_function_call
                 | writeln_statement
                 | readln_statement
                 | break_statement
                 | continue_statement
                 | case_statement
                 | """
    pass

def p_case_statement(t):
    """case_statement : CASE expression OF case_list END"""
    pass

def p_case_list(t):
    """case_list : case_option SEMICOLON case_list
                 | case_option SEMICOLON"""
    pass
def p_case_option(t):
    """case_option : NUMBER COLON statement
                   | BOOL COLON statement
                   | PHRASE COLON statement
                   | ID COLON statement"""
    pass

def p_writeln_statement(t):
    """writeln_statement : WRITELN LPAREN param_list RPAREN
                          | WRITELN LPAREN RPAREN"""
    pass

def p_readln_statement(t):
    """readln_statement : READLN LPAREN id_list RPAREN
                        | READLN LPAREN RPAREN"""
    pass

def p_break_statement(t):
    """break_statement : BREAK SEMICOLON"""
    pass

def p_continue_statement(t):
    """continue_statement : CONTINUE SEMICOLON"""
    pass


def p_procedure_or_function_call(t):
    """procedure_or_function_call : ID LPAREN param_list RPAREN
                                   | ID"""
    pass

def p_param_list(t):
    """param_list : param_list COMMA param
                  | param"""
    pass

def p_param(t):
    """param : expression"""
    pass

def p_if_statement(t):
    """if_statement : IF expression THEN statement ELSE statement
                    | IF expression THEN statement"""
    pass

def p_while_statement(t):
    """while_statement : WHILE expression DO statement"""
    pass

def p_repeat_statement(t):
    """repeat_statement : REPEAT statement UNTIL expression"""
    pass

def p_for_statement(t):
    """for_statement : FOR assignment_statement TO expression DO statement
                     | FOR assignment_statement DOWNTO expression DO statement"""
    pass

def p_assignment_statement(t):
    """assignment_statement : ID ASSIGN expression"""
    pass

def p_expression(t):
    """expression : expression and_or expression_m
                  | expression_m"""
    pass

def p_expression_m(t):
    """expression_m : expression_s
                    | expression_m sign expression_s"""
    pass

def p_expression_s(t):
    """expression_s : element
                    | expression_s psign element"""
    pass

def p_and_or(t):
    """and_or : AND
              | OR"""
    pass

def p_psign(t):
    """psign : TIMES
             | DIVIDE"""
    pass

def p_sign(t):
    """sign : PLUS
            | MINUS
            | DIV
            | MOD
            | EQUALS
            | DIFFERENT
            | LESSTHAN
            | LESSEQUAL
            | GREATERTHAN
            | GREATEREQUAL"""
    pass

def p_element(t):
    """element : ID
               | NUMBER
               | BOOL
               | PHRASE
               | LPAREN expression RPAREN
               | NOT element"""
    pass

def p_error(t):
    if t:
        print(f"Syntax error at '{t.value}', line {t.lineno}")
    else:
        print("Syntax error at EOF")
        
parser = yacc.yacc()

def parse(data):
    result = parser.parse(data)
    return result

def main():
    if len(sys.argv) != 2:
        print("Usage: python pasSyn.py <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        data = file.read()
    parse(data)


if __name__ == "__main__":
    main()
