import sys
from pasAnalex import *
from pasSemantic import *
from ply import yacc

start = 'program'

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'DIV', 'MOD'),
    ('left', 'EQUALS', 'DIFFERENT', 'LESSEQUAL', 'LESSTHAN', 'GREATERTHAN', 'GREATEREQUAL'),
    ('left', 'OR', 'AND'),
)

symbol_table = SymbolTable()

def p_program(t):
    'program : header SEMICOLON block DOT'
    if not symbol_table.report_errors():
        print("Programa contém erros semânticos!")
    else:
        print("Análise semântica concluída com sucesso!")
    print(f"Program: {t[1]} ; {t[3]} .")

def p_header(t):
    'header : PROGRAM ID'
    print(f"Header: PROGRAM {t[2]}")
    symbol_table.add_symbol(t[2], 'program', None, None, t.lineno(2))
    t[0] = t[2]
    t[0] = f"PROGRAM {t[2]}"

def p_block(t):
    """block : variable_declaration_part procedure_or_function statement_part 
               | variable_declaration_part procedure_or_function variable_declaration_part statement_part"""
    if len(t) == 4:
        print(f"Block: {t[1]} {t[2]} {t[3]}")
        t[0] = f"{t[1]} {t[2]} {t[3]}"
    else:
        print(f"Block with additional var declarations: {t[1]} {t[2]} {t[3]} {t[4]}")
        t[0] = f"{t[1]} {t[2]} {t[3]} {t[4]}"

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
    
    id_names = t[1].replace(',', ' ').replace('[', ' ').replace(']', ' ').split()
    ids = [id_name for id_name in id_names if id_name.isalpha()]
    
    for id_name in ids:
        if symbol_table.lookup(id_name) and id_name in symbol_table.scopes[-1]:
            symbol_table.add_error(f"Variável '{id_name}' já declarada neste escopo", t.lineno(1))
        else:
            symbol_table.add_symbol(id_name, 'variable', t[3], None, t.lineno(1))
    
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
    
    # Saindo do escopo do procedimento
    symbol_table.exit_scope()
    # Resetar o tipo de retorno da função atual
    symbol_table.current_function = None
    
    t[0] = f"{t[1]}; {t[3]}"

def p_procedure_heading(t):
    """procedure_heading : PROCEDURE ID
                        | PROCEDURE ID LPAREN parameter_list RPAREN"""
    if len(t) == 3:
        print(f"Procedure heading: PROCEDURE {t[2]}")
        
        symbol_table.add_symbol(t[2], 'procedure', None, [], t.lineno(2))
        
        symbol_table.enter_scope()
        symbol_table.current_function = {'name': t[2], 'kind': 'procedure', 'return_type': None}
        
        t[0] = f"PROCEDURE {t[2]}"
    else:
        print(f"Procedure heading with params: PROCEDURE {t[2]}({t[4]})")
        
        params = []
        param_info = t[4].split(',')
        for param in param_info:
            if ':' in param:
                param_name, param_type = param.split(':')
                param_name = param_name.strip()
                param_type = param_type.strip()
                params.append(Symbol(param_name, 'parameter', param_type))
        
        symbol_table.add_symbol(t[2], 'procedure', None, params, t.lineno(2))
        
        symbol_table.enter_scope()
        symbol_table.current_function = {'name': t[2], 'kind': 'procedure', 'return_type': None}
        
        for param in params:
            symbol_table.add_symbol(param.name, 'parameter', param.data_type, None, t.lineno(2))
        
        t[0] = f"PROCEDURE {t[2]}({t[4]})"

def p_function_declaration(t):
    """function_declaration : function_heading SEMICOLON block"""
    print(f"Function declaration: {t[1]} ; {t[3]}")
    
    # Saindo do escopo da função
    symbol_table.exit_scope()
    # Resetar o tipo de retorno da função atual
    symbol_table.current_function = None
    
    t[0] = f"{t[1]}; {t[3]}"

def p_function_heading(t):
    """function_heading : FUNCTION type
                        | FUNCTION ID COLON type
                        | FUNCTION ID LPAREN parameter_list RPAREN COLON type"""
    if len(t) == 3:
        print(f"Function heading: FUNCTION {t[2]}")
        # Caso inválido, funções precisam de um identificador
        symbol_table.add_error("Função precisa de um identificador", t.lineno(1))
        t[0] = f"FUNCTION {t[2]}"
    elif len(t) == 5:
        print(f"Function heading: FUNCTION {t[2]} : {t[4]}")
        
        # Registrar função na tabela de símbolos
        symbol_table.add_symbol(t[2], 'function', t[4], [], t.lineno(2))
        
        # Criar um novo escopo para a função
        symbol_table.enter_scope()
        symbol_table.current_function = {'name': t[2], 'kind': 'function', 'return_type': t[4]}
        
        t[0] = f"FUNCTION {t[2]} : {t[4]}"
    else:
        print(f"Function heading with params: FUNCTION {t[2]}({t[4]}) : {t[7]}")
        
        # Processar parâmetros
        params = []
        param_info = t[4].split(',')
        for param in param_info:
            if ':' in param:
                param_name, param_type = param.split(':')
                param_name = param_name.strip()
                param_type = param_type.strip()
                params.append(Symbol(param_name, 'parameter', param_type))
        
        # Registrar função na tabela de símbolos
        symbol_table.add_symbol(t[2], 'function', t[7], params, t.lineno(2))
        
        # Criar um novo escopo para a função
        symbol_table.enter_scope()
        symbol_table.current_function = {'name': t[2], 'kind': 'function', 'return_type': t[7]}
        
        # Registrar parâmetros no escopo da função
        for param in params:
            symbol_table.add_symbol(param.name, 'parameter', param.data_type, None, t.lineno(2))
        
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
    # Criar tipo de array para análise semântica
    range_parts = t[3].split('..')
    if len(range_parts) == 2:
        try:
            start_range = int(range_parts[0])
            end_range = int(range_parts[1])
            t[0] = ArrayType(t[6], start_range, end_range)
        except ValueError:
            # Não conseguiu converter para inteiros
            symbol_table.add_error(f"Índices do array devem ser inteiros: {t[3]}", t.lineno(1))
            t[0] = f"ARRAY [{t[3]}] OF {t[6]}"
    else:
        symbol_table.add_error(f"Formato inválido para faixa do array: {t[3]}", t.lineno(1))
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
    
    # Verificar se a expressão do CASE é de um tipo válido
    expr_type = symbol_table.analyze_expression(t[2], symbol_table, t.lineno(1))
    if expr_type not in ['integer', 'char', 'boolean', 'string']:
        symbol_table.add_error(f"Expressão do CASE deve ser do tipo inteiro, caractere, booleano ou string, mas é {expr_type}", t.lineno(1))
    
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
    """break_statement : BREAK"""
    print("Break statement: BREAK")
    t[0] = "BREAK"

def p_continue_statement(t):
    """continue_statement : CONTINUE"""
    print("Continue statement: CONTINUE")
    t[0] = "CONTINUE"

def p_procedure_or_function_call(t):
    """procedure_or_function_call : ID LPAREN param_list RPAREN
                                 | ID LPAREN RPAREN
                                 | ID"""
    if len(t) == 5:
        print(f"Procedure/Function call: {t[1]}({t[3]})")
        t[0] = f"{t[1]}({t[3]})"
    elif len(t) == 4:
        print(f"Procedure/Function call (no params): {t[1]}()")
        t[0] = f"{t[1]}()"
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
    """assignment_statement : ID ASSIGN expression
                            | ID ASSIGN procedure_or_function_call
                            | ID LBRACKET expression RBRACKET ASSIGN expression"""
    if len(t) == 4:
        print(f"Assignment: {t[1]} := {t[3]}")
        t[0] = f"{t[1]} := {t[3]}"
    else:
        print(f"Array assignment: {t[1]}[{t[3]}] := {t[6]}")
        t[0] = f"{t[1]}[{t[3]}] := {t[6]}"

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
               | ID LBRACKET expression RBRACKET
               | procedure_or_function_call"""
    if len(t) == 2:
        print(f"Element: {t[1]}")
        t[0] = t[1]
    elif len(t) == 3:
        print(f"Not element: NOT {t[2]}")
        t[0] = f"NOT {t[2]}"
    elif len(t) == 4:
        print(f"Parenthesized expression: ({t[2]})")
        t[0] = f"({t[2]})"
    elif len(t) == 5:
        if t[1] == 'LENGTH':
            print(f"Length function: LENGTH({t[3]})")
            t[0] = f"LENGTH({t[3]})"
        else:
            print(f"Array element: {t[1]}[{t[3]}]")
            t[0] = f"{t[1]}[{t[3]}]"
    else:
        # This should not be reached, but just in case
        print(f"Unknown element structure")
        t[0] = "Unknown"

def p_error(t):
    if t:
        print(f"Syntax error at '{t.value}', line {t.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc(debug=True)

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
