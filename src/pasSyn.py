import sys
from pasAnalex import *
from ASTNode import *
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
    t[0] = Program(t[1], t[3])

def p_header(t):
    'header : PROGRAM ID'
    t[0] = Header(t[2])

def p_block(t):
    """block : variable_declaration_part procedure_or_function statement_part 
               | variable_declaration_part procedure_or_function variable_declaration_part statement_part"""
    if len(t) == 4:
        t[0] = Block(t[1], t[2], t[3])
    else:
        t[0] = Block(t[1], t[2], t[4], t[3])

def p_variable_declaration_part(t):
    """variable_declaration_part : VAR variable_declaration_list
                                | """
    if len(t) > 1:
        t[0] = VarDeclarationPart(t[2])
    else:
        t[0] = VarDeclarationPart()


def p_variable_declaration_list(t):
    """variable_declaration_list : variable_declaration_list variable_declaration
                                | variable_declaration"""
    if len(t) == 3:
        if isinstance(t[1], list):
            t[0] = t[1] + [t[2]]
        else:
            t[0] = [t[1], t[2]]
    else:
        t[0] = [t[1]]
def p_variable_declaration(t):
    """variable_declaration : id_list COLON type SEMICOLON"""
    t[0] = VarDeclaration(t[1], t[3])

def p_id_list(t):
    """id_list : ID
               | ID LBRACKET expression RBRACKET 
               | ID COMMA id_list
               | ID LBRACKET expression RBRACKET COMMA id_list"""
    if len(t) == 2:
        t[0] = [Identifier(t[1])]
    elif len(t) == 5:
        t[0] = [ArrayId(t[1], t[3])]
    elif len(t) == 4:
        if isinstance(t[3], list):
            t[0] = [Identifier(t[1])] + t[3]
        else:
            t[0] = [Identifier(t[1]), t[3]]
    else:  # len(t) == 7
        if isinstance(t[6], list):
            t[0] = [ArrayId(t[1], t[3])] + t[6]
        else:
            t[0] = [ArrayId(t[1], t[3]), t[6]]

def p_procedure_or_function(t):
    """procedure_or_function : proc_or_func_declaration SEMICOLON procedure_or_function
                            | """
    if len(t) > 1:
        if isinstance(t[3], list):
            t[0] = [t[1]] + t[3]
        else:
            t[0] = [t[1], t[3]] if t[3] else [t[1]]
    else:
        t[0] = []


def p_proc_or_func_declaration(t):
    """proc_or_func_declaration : procedure_declaration
                               | function_declaration"""
    t[0] = t[1]

def p_procedure_declaration(t):
    """procedure_declaration : procedure_heading SEMICOLON block"""
    t[0] = ProcedureDeclaration(t[1], t[3])

def p_procedure_heading(t):
    """procedure_heading : PROCEDURE ID
                        | PROCEDURE ID LPAREN parameter_list RPAREN"""
    if len(t) == 3:
        t[0] = ProcedureHeading(t[2])
    else:
        t[0] = ProcedureHeading(t[2], t[4])

def p_function_declaration(t):
    """function_declaration : function_heading SEMICOLON block"""
    t[0] = FunctionDeclaration(t[1], t[3])

def p_function_heading(t):
    """function_heading : FUNCTION type
                        | FUNCTION ID COLON type
                        | FUNCTION ID LPAREN parameter_list RPAREN COLON type"""
    if len(t) == 3:
        t[0] = FunctionHeading(None, t[2])
    elif len(t) == 5:
        t[0] = FunctionHeading(t[2], t[4])
    else:
        t[0] = FunctionHeading(t[2], t[7], t[4])

def p_parameter_list(t):
    """parameter_list : parameter COMMA parameter_list
                     | parameter"""
    if len(t) == 4:
        if isinstance(t[3], list):
            t[0] = [t[1]] + t[3]
        else:
            t[0] = [t[1], t[3]]
    else:
        t[0] = [t[1]]


def p_parameter(t):
    """parameter : ID COLON type"""
    t[0] = Parameter(t[1], t[3])

def p_type(t):
    """type : REAL
            | INTEGER
            | BOOLEAN
            | STRING
            | array_type"""
    if isinstance(t[1], ASTNode):
        t[0] = t[1]
    else:
        t[0] = Type(t[1])

def p_array_type(t):
    """array_type : ARRAY LBRACKET range RBRACKET OF type"""
    t[0] = ArrayType(t[3], t[6])

def p_range(t):
    """range : expression RANGE expression"""

def p_statement_part(t):
    """statement_part : BEGIN statement_sequence END"""
    t[0] = StatementPart(t[2])

def p_statement_sequence(t):
    """statement_sequence : statement SEMICOLON statement_sequence
                         | statement"""
    if len(t) == 4:
        if isinstance(t[3], StatementSequence):
            t[3].statements.insert(0, t[1])
            t[0] = t[3]
        else:
            t[0] = StatementSequence([t[1], t[3]])
    else:
        t[0] = StatementSequence(t[1])
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
        t[0] = t[1]
    else:
        t[0] = []

def p_case_statement(t):
    """case_statement : CASE expression OF case_list END"""
    print(f"Case statement: CASE {t[2]} OF {t[4]} END")
    t[0] = CaseStatement(t[2], t[4])

def p_case_list(t):
    """case_list : case_option SEMICOLON case_list
                 | case_option SEMICOLON"""
    if len(t) == 4:
        if isinstance(t[3], list):
            t[0] = [t[1]] + t[3]
        else:
            t[0] = [t[1], t[3]]
    else:
        t[0] = [t[1]]


def p_case_option(t):
    """case_option : NUMBER COLON statement
                  | BOOL COLON statement
                  | PHRASE COLON statement
                  | ID COLON statement"""

    if t[1].type == 'NUMBER':
        value = Literal(t[1], 'NUMBER')
    elif t[1].type == 'BOOL':
        value = Literal(t[1], 'BOOL')
    elif t[1].type == 'PHRASE':
        value = Literal(t[1], 'PHRASE')
    else:  # ID
        value = Identifier(t[1])
    
    t[0] = CaseOption(value, t[3])
def p_writeln_statement(t):
    """writeln_statement : WRITELN LPAREN param_list RPAREN
                         | WRITELN LPAREN RPAREN
                         | WRITE LPAREN param_list RPAREN
                         | WRITE LPAREN RPAREN"""
    if len(t) == 5:
        t[0] = WritelnStatement(t[3])
    else:
        t[0] = WritelnStatement()

def p_readln_statement(t):
    """readln_statement : READLN LPAREN id_list RPAREN
                       | READLN LPAREN RPAREN
                       | READ LPAREN id_list RPAREN
                       | READ LPAREN RPAREN"""
    if len(t) == 5:
        t[0] = ReadlnStatement(t[3])
    else:
        t[0] = ReadlnStatement()


def p_break_statement(t):
    """break_statement : BREAK"""
    print("Break statement: BREAK")
    t[0] = BreakStatement()

def p_continue_statement(t):
    """continue_statement : CONTINUE"""
    t[0] = ContinueStatement()

def p_procedure_or_function_call(t):
    """procedure_or_function_call : ID LPAREN param_list RPAREN
                                 | ID LPAREN RPAREN
                                 | ID"""
    if len(t) == 5:
        t[0] = ProcedureCall(t[1], t[3])
    elif len(t) == 4:
        t[0] = ProcedureCall(t[1])
    else:
        t[0] = Identifier(t[1])



def p_param_list(t):
    """param_list : param_list COMMA param
                  | param"""
    if len(t) == 4:
        if isinstance(t[1], list):
            t[0] = t[1] + [t[3]]
        else:
            t[0] = [t[1], t[3]]
    else:
        t[0] = [t[1]]

def p_param(t):
    """param : expression"""
    t[0] = t[1]

def p_if_statement(t):
    """if_statement : IF expression THEN statement ELSE statement
                    | IF expression THEN statement"""
    if len(t) == 7:
        t[0] = IfStatement(t[2], t[4], t[6])
    else:
        t[0] = IfStatement(t[2], t[4])

def p_while_statement(t):
    """while_statement : WHILE expression DO statement"""
    t[0] = WhileStatement(t[2], t[4])

def p_repeat_statement(t):
    """repeat_statement : REPEAT statement UNTIL expression"""
    t[0] = RepeatStatement(t[2], t[4])

def p_for_statement(t):
    """for_statement : FOR assignment_statement TO expression DO statement
                    | FOR assignment_statement DOWNTO expression DO statement"""

    t[0] = ForStatement(t[2], t[3], t[4], t[6])

def p_assignment_statement(t):
    """assignment_statement : ID ASSIGN expression
                            | ID ASSIGN procedure_or_function_call
                            | ID LBRACKET expression RBRACKET ASSIGN expression"""
    if len(t) == 4:
        t[0] = Assignment(Identifier(t[1]), t[3])
    else:
        t[0] = ArrayAssignment(t[1], t[3], t[6])

def p_expression(t):
    """expression : expression and_or expression_m
                  | expression_m"""
    if len(t) == 4:
        t[0] = BinaryOp(t[1], t[2], t[3])
    else:
        t[0] = t[1]

def p_expression_m(t):
    """expression_m : expression_s
                   | expression_m sign expression_s"""
    if len(t) == 4:
        t[0] = BinaryOp(t[1], t[2], t[3])
    else:
        t[0] = t[1]

def p_expression_s(t):
    """expression_s : element
                   | expression_s psign element"""
    if len(t) == 4:
        t[0] = BinaryOp(t[1], t[2], t[3])
    else:
        t[0] = t[1]
def p_and_or(t):
    """and_or : AND
              | OR"""
    t[0] = t[1]

def p_psign(t):
    """psign : TIMES
             | DIVIDE"""
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
    t[0] = t[1]

def p_length_function(t):
    """length_function : LENGTH LPAREN expression RPAREN"""
    t[0] = LengthFunction(t[3])

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
        if isinstance(t[1], ASTNode):
            t[0] = t[1]
        elif isinstance(t[1], (int, float)):
            t[0] = Literal(t[1], 'NUMBER')
        elif t[1] in ('true', 'false'):
            t[0] = Literal(t[1], 'BOOL')
        elif isinstance(t[1], str) and (t[1].startswith('"') or t[1].startswith("'")):
            t[0] = Literal(t[1], 'PHRASE')
        else:
            t[0] = Identifier(t[1])
    elif len(t) == 3:
        t[0] = UnaryOp('NOT', t[2])
    elif len(t) == 4:
        t[0] = t[2]  
    elif len(t) == 5:
        if t[1] == 'LENGTH':
            t[0] = LengthFunction(t[3])
        else:
            t[0] = ArrayId(t[1], t[3])
    else:
        t[0] = None

def p_error(t):
    if t:
        print(f"Syntax error at '{t.value}', line {t.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc(debug=True)

def print_ast(node, indent=0):
    if node is None:
        return "None"
    
    indent_str = "  " * indent
    
    if isinstance(node, list):
        result = "[\n"
        for item in node:
            result += f"{indent_str}  {print_ast(item, indent + 1)},\n"
        result += f"{indent_str}]"
        return result
    
    if not isinstance(node, ASTNode):
        return str(node)
    
    class_name = node.__class__.__name__
    
    attrs = []
    for attr_name in dir(node):
        if attr_name.startswith('_') or callable(getattr(node, attr_name)):
            continue
        
        attr_value = getattr(node, attr_name)
        attrs.append(f"{attr_name}={print_ast(attr_value, indent + 1)}")
    
    if attrs:
        attrs_str = ",\n".join(f"{indent_str}  {attr}" for attr in attrs)
        return f"{class_name}(\n{attrs_str}\n{indent_str})"
    else:
        return f"{class_name}()"


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
    print("\nAST result:")
    ast = print_ast(result)
    print(ast)
    return result

if __name__ == "__main__":
    main()
