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
    print(f"Program: {t[1]} ; {t[3]} .")

def p_header(t):
    'header : PROGRAM ID'
    print(f"Header: PROGRAM {t[2]}")
    t[0] = f"PROGRAM {t[2]}"

def p_block(t):
    """block : variable_declaration_part procedure_or_function statement_part"""
    print(f"Block: {t[1]} {t[2]} {t[3]}")
    t[0] = f"{t[1]} {t[2]} {t[3]}"

def p_variable_declaration_part(t):
    """variable_declaration_part : VAR variable_declaration_list
                                | """
    if len(t) > 1:
        print(f"Variable declaration part: VAR {t[2]}")
        t[0] = f"VAR {t[2]}"
    else:
        print("Empty variable declaration part")
        t[0] = ""

def p_variable_declaration_list(t):
    """variable_declaration_list : variable_declaration_list variable_declaration
                                | variable_declaration"""
    if len(t) == 3:
        print(f"Variable declaration list: {t[1]} {t[2]}")
        t[0] = f"{t[1]} {t[2]}"
    else:
        print(f"Variable declaration: {t[1]}")
        t[0] = t[1]

def p_variable_declaration(t):
    """variable_declaration : id_list COLON type SEMICOLON"""
    print(f"Variable declaration: {t[1]} : {t[3]} ;")
    t[0] = f"{t[1]} : {t[3]};"

def p_id_list(t):
    """id_list : ID
               | ID LBRACKET expression RBRACKET 
               | ID COMMA id_list
               | ID LBRACKET expression RBRACKET COMMA id_list"""
    if len(t) == 2:
        print(f"ID: {t[1]}")
        t[0] = t[1]
    elif len(t) == 5:
        print(f"Array ID: {t[1]}[{t[3]}]")
        t[0] = f"{t[1]}[{t[3]}]"
    elif len(t) == 4:
        print(f"ID list: {t[1]}, {t[3]}")
        t[0] = f"{t[1]}, {t[3]}"
    else:
        print(f"Array ID list: {t[1]}[{t[3]}], {t[6]}")
        t[0] = f"{t[1]}[{t[3]}], {t[6]}"

def p_procedure_or_function(t):
    """procedure_or_function : proc_or_func_declaration SEMICOLON procedure_or_function
                            | """
    if len(t) > 1:
        print(f"Procedure/Function: {t[1]} ; {t[3]}")
        t[0] = f"{t[1]}; {t[3]}"
    else:
        print("Empty procedure/function part")
        t[0] = ""

def p_proc_or_func_declaration(t):
    """proc_or_func_declaration : procedure_declaration
                               | function_declaration"""
    print(f"Proc/Func declaration: {t[1]}")
    t[0] = t[1]

def p_procedure_declaration(t):
    """procedure_declaration : procedure_heading SEMICOLON block"""
    print(f"Procedure declaration: {t[1]} ; {t[3]}")
    t[0] = f"{t[1]}; {t[3]}"

def p_procedure_heading(t):
    """procedure_heading : PROCEDURE ID
                        | PROCEDURE ID LPAREN parameter_list RPAREN"""
    if len(t) == 3:
        print(f"Procedure heading: PROCEDURE {t[2]}")
        t[0] = f"PROCEDURE {t[2]}"
    else:
        print(f"Procedure heading with params: PROCEDURE {t[2]}({t[4]})")
        t[0] = f"PROCEDURE {t[2]}({t[4]})"

def p_function_declaration(t):
    """function_declaration : function_heading SEMICOLON block"""
    print(f"Function declaration: {t[1]} ; {t[3]}")
    t[0] = f"{t[1]}; {t[3]}"

def p_function_heading(t):
    """function_heading : FUNCTION type
                        | FUNCTION ID COLON type
                        | FUNCTION ID LPAREN parameter_list RPAREN COLON type"""
    if len(t) == 3:
        print(f"Function heading: FUNCTION {t[2]}")
        t[0] = f"FUNCTION {t[2]}"
    elif len(t) == 5:
        print(f"Function heading: FUNCTION {t[2]} : {t[4]}")
        t[0] = f"FUNCTION {t[2]} : {t[4]}"
    else:
        print(f"Function heading with params: FUNCTION {t[2]}({t[4]}) : {t[7]}")
        t[0] = f"FUNCTION {t[2]}({t[4]}) : {t[7]}"

def p_parameter_list(t):
    """parameter_list : parameter COMMA parameter_list
                     | parameter"""
    if len(t) == 4:
        print(f"Parameter list: {t[1]}, {t[3]}")
        t[0] = f"{t[1]}, {t[3]}"
    else:
        print(f"Parameter: {t[1]}")
        t[0] = t[1]

def p_parameter(t):
    """parameter : ID COLON type"""
    print(f"Parameter: {t[1]} : {t[3]}")
    t[0] = f"{t[1]} : {t[3]}"

def p_type(t):
    """type : REAL
            | INTEGER
            | BOOLEAN
            | STRING
            | array_type"""
    print(f"Type: {t[1]}")
    t[0] = t[1]

def p_array_type(t):
    """array_type : ARRAY LBRACKET range RBRACKET OF type"""
    print(f"Array type: ARRAY [{t[3]}] OF {t[6]}")
    t[0] = f"ARRAY [{t[3]}] OF {t[6]}"

def p_range(t):
    """range : expression RANGE expression"""
    print(f"Range: {t[1]}..{t[3]}")
    t[0] = f"{t[1]}..{t[3]}"

def p_statement_part(t):
    """statement_part : BEGIN statement_sequence END"""
    print(f"Statement part: BEGIN {t[2]} END")
    t[0] = f"BEGIN {t[2]} END"

def p_statement_sequence(t):
    """statement_sequence : statement SEMICOLON statement_sequence
                         | statement"""
    if len(t) == 4:
        print(f"Statement sequence: {t[1]} ; {t[3]}")
        t[0] = f"{t[1]}; {t[3]}"
    else:
        print(f"Statement: {t[1]}")
        t[0] = t[1]

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
    if len(t) > 1:
        print(f"Statement: {t[1]}")
        t[0] = t[1]
    else:
        print("Empty statement")
        t[0] = ""

def p_case_statement(t):
    """case_statement : CASE expression OF case_list END"""
    print(f"Case statement: CASE {t[2]} OF {t[4]} END")
    t[0] = f"CASE {t[2]} OF {t[4]} END"

def p_case_list(t):
    """case_list : case_option SEMICOLON case_list
                 | case_option SEMICOLON"""
    if len(t) == 4:
        print(f"Case list: {t[1]} ; {t[3]}")
        t[0] = f"{t[1]}; {t[3]}"
    else:
        print(f"Case option: {t[1]} ;")
        t[0] = f"{t[1]};"

def p_case_option(t):
    """case_option : NUMBER COLON statement
                  | BOOL COLON statement
                  | PHRASE COLON statement
                  | ID COLON statement"""
    print(f"Case option: {t[1]} : {t[3]}")
    t[0] = f"{t[1]} : {t[3]}"

def p_writeln_statement(t):
    """writeln_statement : WRITELN LPAREN param_list RPAREN
                         | WRITELN LPAREN RPAREN"""
    if len(t) == 5:
        print(f"Writeln: WRITELN({t[3]})")
        t[0] = f"WRITELN({t[3]})"
    else:
        print("Writeln: WRITELN()")
        t[0] = "WRITELN()"

def p_readln_statement(t):
    """readln_statement : READLN LPAREN id_list RPAREN
                       | READLN LPAREN RPAREN"""
    if len(t) == 5:
        print(f"Readln: READLN({t[3]})")
        t[0] = f"READLN({t[3]})"
    else:
        print("Readln: READLN()")
        t[0] = "READLN()"

def p_break_statement(t):
    """break_statement : BREAK SEMICOLON"""
    print("Break statement: BREAK;")
    t[0] = "BREAK;"

def p_continue_statement(t):
    """continue_statement : CONTINUE SEMICOLON"""
    print("Continue statement: CONTINUE;")
    t[0] = "CONTINUE;"

def p_procedure_or_function_call(t):
    """procedure_or_function_call : ID LPAREN param_list RPAREN
                                 | ID"""
    if len(t) == 5:
        print(f"Procedure/Function call: {t[1]}({t[3]})")
        t[0] = f"{t[1]}({t[3]})"
    else:
        print(f"ID call: {t[1]}")
        t[0] = t[1]

def p_param_list(t):
    """param_list : param_list COMMA param
                  | param"""
    if len(t) == 4:
        print(f"Param list: {t[1]}, {t[3]}")
        t[0] = f"{t[1]}, {t[3]}"
    else:
        print(f"Param: {t[1]}")
        t[0] = t[1]

def p_param(t):
    """param : expression"""
    print(f"Param: {t[1]}")
    t[0] = t[1]

def p_if_statement(t):
    """if_statement : IF expression THEN statement ELSE statement
                    | IF expression THEN statement"""
    if len(t) == 7:
        print(f"If statement: IF {t[2]} THEN {t[4]} ELSE {t[6]}")
        t[0] = f"IF {t[2]} THEN {t[4]} ELSE {t[6]}"
    else:
        print(f"If statement: IF {t[2]} THEN {t[4]}")
        t[0] = f"IF {t[2]} THEN {t[4]}"

def p_while_statement(t):
    """while_statement : WHILE expression DO statement"""
    print(f"While statement: WHILE {t[2]} DO {t[4]}")
    t[0] = f"WHILE {t[2]} DO {t[4]}"

def p_repeat_statement(t):
    """repeat_statement : REPEAT statement UNTIL expression"""
    print(f"Repeat statement: REPEAT {t[2]} UNTIL {t[4]}")
    t[0] = f"REPEAT {t[2]} UNTIL {t[4]}"

def p_for_statement(t):
    """for_statement : FOR assignment_statement TO expression DO statement
                    | FOR assignment_statement DOWNTO expression DO statement"""
    if t[3] == 'TO':
        print(f"For statement: FOR {t[2]} TO {t[4]} DO {t[6]}")
        t[0] = f"FOR {t[2]} TO {t[4]} DO {t[6]}"
    else:
        print(f"For statement: FOR {t[2]} DOWNTO {t[4]} DO {t[6]}")
        t[0] = f"FOR {t[2]} DOWNTO {t[4]} DO {t[6]}"

def p_assignment_statement(t):
    """assignment_statement : ID ASSIGN expression"""
    print(f"Assignment: {t[1]} := {t[3]}")
    t[0] = f"{t[1]} := {t[3]}"

def p_expression(t):
    """expression : expression and_or expression_m
                  | expression_m"""
    if len(t) == 4:
        print(f"Expression: {t[1]} {t[2]} {t[3]}")
        t[0] = f"{t[1]} {t[2]} {t[3]}"
    else:
        print(f"Expression_m: {t[1]}")
        t[0] = t[1]

def p_expression_m(t):
    """expression_m : expression_s
                   | expression_m sign expression_s"""
    if len(t) == 4:
        print(f"Expression_m: {t[1]} {t[2]} {t[3]}")
        t[0] = f"{t[1]} {t[2]} {t[3]}"
    else:
        print(f"Expression_s: {t[1]}")
        t[0] = t[1]

def p_expression_s(t):
    """expression_s : element
                   | expression_s psign element"""
    if len(t) == 4:
        print(f"Expression_s: {t[1]} {t[2]} {t[3]}")
        t[0] = f"{t[1]} {t[2]} {t[3]}"
    else:
        print(f"Element: {t[1]}")
        t[0] = t[1]

def p_and_or(t):
    """and_or : AND
              | OR"""
    print(f"And/Or: {t[1]}")
    t[0] = t[1]

def p_psign(t):
    """psign : TIMES
             | DIVIDE"""
    print(f"Psign: {t[1]}")
    t[0] = t[1]

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
    print(f"Sign: {t[1]}")
    t[0] = t[1]

def p_length_function(t):
    """length_function : LENGTH LPAREN expression RPAREN"""
    print(f"Length function: LENGTH({t[3]})")
    t[0] = f"LENGTH({t[3]})"

def p_element(t):
    """element : ID
               | NUMBER
               | BOOL
               | PHRASE
               | LPAREN expression RPAREN
               | NOT element
               | length_function
               | ID LBRACKET expression RBRACKET"""
    if len(t) == 2:
        print(f"Element: {t[1]}")
        t[0] = t[1]
    elif len(t) == 3:
        print(f"Not element: NOT {t[2]}")
        t[0] = f"NOT {t[2]}"
    elif len(t) == 4:
        print(f"Parenthesized expression: ({t[2]})")
        t[0] = f"({t[2]})"
    else:
        print(f"Array element: {t[1]}[{t[3]}]")
        t[0] = f"{t[1]}[{t[3]}]"

def p_error(t):
    if t:
        print(f"Syntax error at '{t.value}', line {t.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

def main():
    if len(sys.argv) != 2:
        print("Usage: python pasSyn.py <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        data = file.read()
    print(f"\nParsing file: {filename}\n")
    result = parser.parse(data)
    print("\nParsing completed successfully!")
    print("\nFinal result:")
    print(result)

if __name__ == "__main__":
    main()
