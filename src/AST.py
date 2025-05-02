class ASTNode:
    """Classe base para todos os nós da Árvore Sintática Abstrata"""
    pass

class ProgramNode(ASTNode):
    """Representa o programa completo"""
    def __init__(self, name, block):
        self.name = name      # Nome do programa
        self.block = block    # Bloco principal do programa
    
    def __str__(self):
        return f"Program: {self.name}"

class BlockNode(ASTNode):
    """Representa um bloco de código"""
    def __init__(self, variables, procedures_functions, statements):
        self.variables = variables or []                   # Lista de declarações de variáveis
        self.procedures_functions = procedures_functions or []  # Lista de procedimentos e funções
        self.statements = statements                 # Bloco de instruções
    
    def __str__(self):
        return f"Block: {len(self.variables)} vars, {len(self.procedures_functions)} funcs/procs"

class VarDeclarationNode(ASTNode):
    """Representa uma declaração de variável"""
    def __init__(self, identifiers, type_node):
        self.identifiers = identifiers   # Lista de nomes de variáveis
        self.type_node = type_node       # Tipo das variáveis
    
    def __str__(self):
        return f"VarDecl: {', '.join(self.identifiers)} : {self.type_node}"

class TypeNode(ASTNode):
    """Classe base para tipos"""
    pass

class SimpleTypeNode(TypeNode):
    """Representa um tipo simples (integer, real, boolean, string)"""
    def __init__(self, type_name):
        self.type_name = type_name  # Nome do tipo
    
    def __str__(self):
        return f"{self.type_name}"

class ArrayTypeNode(TypeNode):
    """Representa um tipo array"""
    def __init__(self, range_node, element_type):
        self.range = range_node       # Intervalo do array (e.g., 1..10)
        self.element_type = element_type  # Tipo dos elementos
    
    def __str__(self):
        return f"array[{self.range}] of {self.element_type}"

class RangeNode(ASTNode):
    """Representa um range para arrays"""
    def __init__(self, start, end):
        self.start = start  # Expressão de início
        self.end = end      # Expressão de fim
    
    def __str__(self):
        return f"{self.start}..{self.end}"

class StatementPartNode(ASTNode):
    """Representa um bloco de instruções (begin...end)"""
    def __init__(self, statements):
        self.statements = statements or []  # Lista de instruções
    
    def __str__(self):
        return f"StatementPart: {len(self.statements)} statements"

class StatementNode(ASTNode):
    """Classe base para todas as instruções"""
    pass

class AssignmentNode(StatementNode):
    """Representa uma atribuição"""
    def __init__(self, target, expression):
        self.target = target        # Variável alvo
        self.expression = expression  # Expressão a ser atribuída
    
    def __str__(self):
        return f"Assign: {self.target} := {self.expression}"

class IfNode(StatementNode):
    """Representa uma instrução if"""
    def __init__(self, condition, then_part, else_part=None):
        self.condition = condition    # Condição
        self.then_part = then_part    # Bloco then
        self.else_part = else_part    # Bloco else (opcional)
    
    def __str__(self):
        return f"If: {self.condition} then..."

class WhileNode(StatementNode):
    """Representa um loop while"""
    def __init__(self, condition, body):
        self.condition = condition  # Condição de continuação
        self.body = body            # Corpo do loop
    
    def __str__(self):
        return f"While: {self.condition} do..."

class RepeatNode(StatementNode):
    """Representa um loop repeat-until"""
    def __init__(self, body, condition):
        self.body = body            # Corpo do loop
        self.condition = condition  # Condição de término
    
    def __str__(self):
        return f"Repeat: ... until {self.condition}"

class ForNode(StatementNode):
    """Representa um loop for"""
    def __init__(self, assignment, direction, limit, body):
        self.assignment = assignment  # Atribuição inicial (inicialização da variável)
        self.direction = direction    # 'to' ou 'downto'
        self.limit = limit            # Expressão de limite
        self.body = body              # Corpo do loop
    
    def __str__(self):
        return f"For: {self.assignment} {self.direction} {self.limit} do..."

class ProcedureCallNode(StatementNode):
    """Representa uma chamada de procedimento"""
    def __init__(self, name, arguments=None):
        self.name = name          # Nome do procedimento
        self.arguments = arguments or []  # Lista de argumentos
    
    def __str__(self):
        return f"Call: {self.name}(...)"

class WritelnNode(StatementNode):
    """Representa uma instrução writeln"""
    def __init__(self, expressions=None):
        self.expressions = expressions or []  # Lista de expressões a serem impressas
    
    def __str__(self):
        return f"Writeln: {len(self.expressions)} expressions"

class ReadlnNode(StatementNode):
    """Representa uma instrução readln"""
    def __init__(self, variables=None):
        self.variables = variables or []  # Lista de variáveis para leitura
    
    def __str__(self):
        return f"Readln: {len(self.variables)} variables"

class BreakNode(StatementNode):
    """Representa uma instrução break"""
    def __str__(self):
        return "Break"

class ContinueNode(StatementNode):
    """Representa uma instrução continue"""
    def __str__(self):
        return "Continue"

class CaseNode(StatementNode):
    """Representa uma instrução case"""
    def __init__(self, expression, case_options):
        self.expression = expression        # Expressão do case
        self.case_options = case_options    # Lista de opções case
    
    def __str__(self):
        return f"Case: {self.expression} of ..."

class CaseOptionNode(ASTNode):
    """Representa uma opção em uma instrução case"""
    def __init__(self, value, statement):
        self.value = value        # Valor do case
        self.statement = statement  # Instrução a ser executada
    
    def __str__(self):
        return f"CaseOption: {self.value}: ..."

class ExpressionNode(ASTNode):
    """Classe base para expressões"""
    pass

class BinaryOpNode(ExpressionNode):
    """Representa uma operação binária"""
    def __init__(self, left, operator, right):
        self.left = left          # Operando esquerdo
        self.operator = operator  # Operador (+, -, *, /, etc.)
        self.right = right        # Operando direito
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

class UnaryOpNode(ExpressionNode):
    """Representa uma operação unária"""
    def __init__(self, operator, operand):
        self.operator = operator  # Operador (not, -)
        self.operand = operand    # Operando
    
    def __str__(self):
        return f"{self.operator}{self.operand}"

class VariableNode(ExpressionNode):
    """Representa uma referência a uma variável"""
    def __init__(self, name):
        self.name = name  # Nome da variável
    
    def __str__(self):
        return self.name

class ArrayAccessNode(ExpressionNode):
    """Representa acesso a um elemento de array"""
    def __init__(self, array_name, index):
        self.array_name = array_name  # Nome do array
        self.index = index            # Índice
    
    def __str__(self):
        return f"{self.array_name}[{self.index}]"

class NumberNode(ExpressionNode):
    """Representa um literal numérico"""
    def __init__(self, value):
        self.value = value  # Valor numérico
    
    def __str__(self):
        return str(self.value)

class StringNode(ExpressionNode):
    """Representa um literal string"""
    def __init__(self, value):
        self.value = value  # Valor da string
    
    def __str__(self):
        return f"'{self.value}'"

class BooleanNode(ExpressionNode):
    """Representa um literal boolean"""
    def __init__(self, value):
        self.value = value  # True ou False
    
    def __str__(self):
        return str(self.value).lower()

class FunctionCallNode(ExpressionNode):
    """Representa uma chamada de função"""
    def __init__(self, name, arguments=None):
        self.name = name          # Nome da função
        self.arguments = arguments or []  # Lista de argumentos
    
    def __str__(self):
        return f"{self.name}(...)"

class ProcedureNode(ASTNode):
    """Representa a declaração de um procedimento"""
    def __init__(self, name, parameters=None, block=None):
        self.name = name          # Nome do procedimento
        self.parameters = parameters or []  # Lista de parâmetros
        self.block = block        # Bloco do procedimento
    
    def __str__(self):
        return f"Procedure: {self.name}"

class FunctionNode(ASTNode):
    """Representa a declaração de uma função"""
    def __init__(self, name, parameters=None, return_type=None, block=None):
        self.name = name            # Nome da função
        self.parameters = parameters or []  # Lista de parâmetros
        self.return_type = return_type  # Tipo de retorno
        self.block = block          # Bloco da função
    
    def __str__(self):
        return f"Function: {self.name} : {self.return_type}"

class ParameterNode(ASTNode):
    """Representa um parâmetro de função ou procedimento"""
    def __init__(self, name, param_type):
        self.name = name          # Nome do parâmetro
        self.param_type = param_type  # Tipo do parâmetro
    
    def __str__(self):
        return f"{self.name}: {self.param_type}"