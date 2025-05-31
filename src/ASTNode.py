class ASTNode:
    def __repr__(self):
        return self.__str__()

class Program(ASTNode):
    def __init__(self, header, block):
        self.header = header
        self.block = block
    
    def __str__(self):
        return f"Program({self.header}, {self.block})"

class Header(ASTNode):
    def __init__(self, program_name):
        self.program_name = program_name
    
    def __str__(self):
        return f"Header(PROGRAM {self.program_name})"

class Block(ASTNode):
    def __init__(self, var_decl_part, proc_func_part, statement_part, extra_var_decl=None):
        self.var_decl_part = var_decl_part
        self.proc_func_part = proc_func_part
        self.statement_part = statement_part
        self.extra_var_decl = extra_var_decl
    
    def __str__(self):
        if self.extra_var_decl:
            return f"Block({self.var_decl_part}, {self.proc_func_part}, {self.extra_var_decl}, {self.statement_part})"
        return f"Block({self.var_decl_part}, {self.proc_func_part}, {self.statement_part})"

class VarDeclarationPart(ASTNode):
    def __init__(self, declarations=None):
        self.declarations = declarations or []
    
    def __str__(self):
        return f"VarDeclarationPart({self.declarations})"

class VarDeclaration(ASTNode):
    def __init__(self, id_list, type_name):
        self.id_list = id_list
        self.type_name = type_name
    
    def __str__(self):
        return f"VarDeclaration({self.id_list}, {self.type_name})"

class IdList(ASTNode):
    def __init__(self, ids):
        self.ids = ids
    
    def __str__(self):
        return f"IdList({self.ids})"

class ArrayId(ASTNode):
    def __init__(self, id_name, expression):
        self.id_name = id_name
        self.expression = expression
    
    def __str__(self):
        return f"ArrayId({self.id_name}, {self.expression})"

class Type(ASTNode):
    def __init__(self, type_name):
        self.type_name = type_name
    
    def __str__(self):
        return f"Type({self.type_name})"

class ArrayType(ASTNode):
    def __init__(self, range_node, element_type):
        self.range = range_node
        self.element_type = element_type
    
    def __str__(self):
        return f"ArrayType({self.range}, {self.element_type})"

class Range(ASTNode):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __str__(self):
        return f"Range({self.start}, {self.end})"

class StatementPart(ASTNode):
    def __init__(self, statement_sequence):
        self.statement_sequence = statement_sequence
    
    def __str__(self):
        return f"StatementPart({self.statement_sequence})"

class StatementSequence(ASTNode):
    def __init__(self, statements):
        self.statements = statements if isinstance(statements, list) else [statements]
    
    def __str__(self):
        return f"StatementSequence({self.statements})"

class Assignment(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value
    
    def __str__(self):
        return f"Assignment({self.target}, {self.value})"

class ArrayAssignment(ASTNode):
    def __init__(self, array_id, index, value):
        self.array_id = array_id
        self.index = index
        self.value = value
    
    def __str__(self):
        return f"ArrayAssignment({self.array_id}, {self.index}, {self.value})"

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"BinaryOp({self.left}, {self.operator}, {self.right})"

class UnaryOp(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
    
    def __str__(self):
        return f"UnaryOp({self.operator}, {self.operand})"

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def __str__(self):
        if self.else_branch:
            return f"IfStatement({self.condition}, {self.then_branch}, {self.else_branch})"
        return f"IfStatement({self.condition}, {self.then_branch})"

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def __str__(self):
        return f"WhileStatement({self.condition}, {self.body})"

class RepeatStatement(ASTNode):
    def __init__(self, body, condition):
        self.body = body
        self.condition = condition
    
    def __str__(self):
        return f"RepeatStatement({self.body}, {self.condition})"

class ForStatement(ASTNode):
    def __init__(self, init, direction, limit, body):
        self.init = init
        self.direction = direction 
        self.limit = limit
        self.body = body
    
    def __str__(self):
        return f"ForStatement({self.init}, {self.direction}, {self.limit}, {self.body})"

class ProcedureCall(ASTNode):
    def __init__(self, procedure_name, params=None):
        self.procedure_name = procedure_name
        self.params = params or []
    
    def __str__(self):
        return f"ProcedureCall({self.procedure_name}, {self.params})"

class FunctionCall(ASTNode):
    def __init__(self, function_name, params=None):
        self.function_name = function_name
        self.params = params or []
    
    def __str__(self):
        return f"FunctionCall({self.function_name}, {self.params})"

class WritelnStatement(ASTNode):
    def __init__(self, params=None):
        self.params = params or []
    
    def __str__(self):
        return f"WritelnStatement({self.params})"

class ReadlnStatement(ASTNode):
    def __init__(self, params=None):
        self.params = params or []
    
    def __str__(self):
        return f"ReadlnStatement({self.params})"

class BreakStatement(ASTNode):
    def __str__(self):
        return "BreakStatement()"

class ContinueStatement(ASTNode):
    def __str__(self):
        return "ContinueStatement()"

class CaseStatement(ASTNode):
    def __init__(self, expression, case_list):
        self.expression = expression
        self.case_list = case_list
    
    def __str__(self):
        return f"CaseStatement({self.expression}, {self.case_list})"

class CaseOption(ASTNode):
    def __init__(self, value, statement):
        self.value = value
        self.statement = statement
    
    def __str__(self):
        return f"CaseOption({self.value}, {self.statement})"

class Literal(ASTNode):
    def __init__(self, value, type_name):
        self.value = value
        self.type_name = type_name 
    
    def __str__(self):
        return f"Literal({self.value}, {self.type_name})"

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Identifier({self.name})"

class LengthFunction(ASTNode):
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return f"LengthFunction({self.expression})"

class ProcedureDeclaration(ASTNode):
    def __init__(self, heading, block):
        self.heading = heading
        self.block = block
    
    def __str__(self):
        return f"ProcedureDeclaration({self.heading}, {self.block})"

class ProcedureHeading(ASTNode):
    def __init__(self, name, params=None):
        self.name = name
        self.params = params or []
    
    def __str__(self):
        return f"ProcedureHeading({self.name}, {self.params})"

class FunctionDeclaration(ASTNode):
    def __init__(self, heading, block):
        self.heading = heading
        self.block = block
    
    def __str__(self):
        return f"FunctionDeclaration({self.heading}, {self.block})"

class FunctionHeading(ASTNode):
    def __init__(self, name, return_type, params=None):
        self.name = name
        self.return_type = return_type
        self.params = params or []
    
    def __str__(self):
        return f"FunctionHeading({self.name}, {self.return_type}, {self.params})"

class Parameter(ASTNode):
    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
    
    def __str__(self):
        return f"Parameter({self.name}, {self.type_name})"
