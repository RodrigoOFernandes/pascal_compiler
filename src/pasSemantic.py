class Symbol:
    def __init__(self, name, kind, data_type=None, params=None, line_num=None):
        self.name = name         # Nome do símbolo (variável/função/procedimento)
        self.kind = kind         # 'variable', 'function', 'procedure', 'parameter'
        self.data_type = data_type   # 'integer', 'real', 'boolean', 'string', ou um tipo array
        self.params = params or []   # Lista de parâmetros (apenas para funções/procedimentos)
        self.line_num = line_num     # Linha onde o símbolo foi declarado
        self.initialized = False     # Indica se uma variável foi inicializada
        self.used = False            # Indica se um símbolo foi usado

    def __str__(self):
        params_str = ", ".join([f"{p.name}: {p.data_type}" for p in self.params]) if self.params else ""
        return f"{self.name} [{self.kind}] - Type: {self.data_type}" + (f" Params: ({params_str})" if self.params else "")

class ArrayType:
    def __init__(self, base_type, start_range, end_range):
        self.base_type = base_type       # Tipo base do array (integer, real, etc)
        self.start_range = start_range   # Início da faixa de índices
        self.end_range = end_range       # Fim da faixa de índices
    
    def __str__(self):
        return f"ARRAY[{self.start_range}..{self.end_range}] OF {self.base_type}"

class SymbolTable:
    def __init__(self):
        self.scopes = [{}] 
        self.current_function = None 
        self.errors = []
        
    def enter_scope(self):
        """Entra em um novo escopo (função, procedimento, bloco)"""
        self.scopes.append({})
        
    def exit_scope(self):
        """Sai do escopo atual"""
        if len(self.scopes) > 1:  
            for name, symbol in self.scopes[-1].items():
                if symbol.kind == 'variable' and not symbol.used:
                    self.add_warning(f"Variável '{name}' declarada mas nunca utilizada")
            self.scopes.pop()
    
    def add_symbol(self, name, kind, data_type=None, params=None, line_num=None):
        """Adiciona um símbolo ao escopo atual"""
        if name in self.scopes[-1]:
            self.add_error(f"Redeclaração de '{name}' no mesmo escopo", line_num)
            return False
            
        self.scopes[-1][name] = Symbol(name, kind, data_type, params, line_num)
        return True
        
    def lookup(self, name):
        """Procura um símbolo em todos os escopos, começando pelo mais interno"""
        for scope in reversed(self.scopes):
            if name in scope:
                symbol = scope[name]
                symbol.used = True  # Marcar como usado quando consultado
                return symbol
        return None
    
    def add_error(self, message, line_num=None):
        """Adiciona uma mensagem de erro"""
        location = f" na linha {line_num}" if line_num else ""
        self.errors.append(f"ERRO{location}: {message}")
        
    def add_warning(self, message, line_num=None):
        """Adiciona um aviso"""
        location = f" na linha {line_num}" if line_num else ""
        self.errors.append(f"AVISO{location}: {message}")
    
    def check_types(self, type1, type2, operation=None, line_num=None):
        """Verifica compatibilidade de tipos em operações"""
        if isinstance(type1, str) and isinstance(type2, str):
            if type1 == type2:
                return type1
                
            if operation in ['+', '-', '*', '/'] and type1 == 'integer' and type2 == 'real':
                return 'real'
            if operation in ['+', '-', '*', '/'] and type1 == 'real' and type2 == 'integer':
                return 'real'
                
            if operation in ['=', '<>', '<', '<=', '>', '>=']:
                if (type1 in ['integer', 'real'] and type2 in ['integer', 'real']):
                    return 'boolean'
                if type1 == type2: 
                    return 'boolean'
                    
            if operation in ['and', 'or'] and type1 == 'boolean' and type2 == 'boolean':
                return 'boolean'
                
            if operation == '+' and type1 == 'string' and type2 == 'string':
                return 'string'
                
            self.add_error(f"Tipos incompatíveis: {type1} {operation} {type2}", line_num)
            return None
        
        if isinstance(type1, ArrayType) and isinstance(type2, ArrayType):
            if operation == '=':
                if (type1.base_type == type2.base_type and 
                    type1.start_range == type2.start_range and 
                    type1.end_range == type2.end_range):
                    return type1
            self.add_error(f"Tipos de array incompatíveis", line_num)
            return None
            
        self.add_error(f"Tipos incompatíveis em operação", line_num)
        return None
        
    def verify_identifier(self, id_name, context=None, line_num=None):
        """Verifica se um identificador está declarado e é utilizado no contexto correto"""
        symbol = self.lookup(id_name)
        if not symbol:
            self.add_error(f"Identificador '{id_name}' não declarado", line_num)
            return None
            
        if context == 'function_call' and symbol.kind not in ['function', 'procedure']:
            self.add_error(f"'{id_name}' não é uma função ou procedimento", line_num)
            return None
        elif context == 'variable' and symbol.kind not in ['variable', 'parameter']:
            self.add_error(f"'{id_name}' não é uma variável", line_num)
            return None
            
        return symbol
        
    def report_errors(self):
        """Exibe todos os erros e avisos coletados"""
        if not self.errors:
            print("Análise semântica concluída sem erros.")
            return True
        else:
            for error in self.errors:
                print(error)
            return False

def get_literal_type(literal):
    """Identifica o tipo de um literal"""
    try:
        int(literal)
        return 'integer'
    except ValueError:
        try:
            float(literal)
            return 'real'
        except ValueError:
            if literal.lower() in ['true', 'false']:
                return 'boolean'
            if literal.startswith('"') or literal.startswith("'"):
                return 'string'
    return None

def is_numeric_type(type_name):
    """Verifica se um tipo é numérico"""
    return type_name in ['integer', 'real']

def analyze_expression(expr, symbol_table, line_num=None):
    """Analisa o tipo de uma expressão"""
    if expr.isalpha():
        symbol = symbol_table.verify_identifier(expr, 'variable', line_num)
        return symbol.data_type if symbol else None
        
    if expr.isdigit() or expr in ['true', 'false'] or (expr.startswith('"') and expr.endswith('"')):
        return get_literal_type(expr)

    operators = ['+', '-', '*', '/', 'and', 'or', '=', '<>', '<', '<=', '>', '>=']
    for op in operators:
        if op in expr:
            parts = expr.split(op, 1)
            left_type = analyze_expression(parts[0].strip(), symbol_table, line_num)
            right_type = analyze_expression(parts[1].strip(), symbol_table, line_num)
            return symbol_table.check_types(left_type, right_type, op, line_num)
            
    if '(' in expr and ')' in expr:
        func_name = expr.split('(')[0].strip()
        symbol = symbol_table.verify_identifier(func_name, 'function_call', line_num)
        return symbol.data_type if symbol else None
        
    symbol_table.add_error(f"Não foi possível determinar o tipo da expressão: {expr}", line_num)
    return None

def resolve_type(type_str, symbol_table, line_num=None):
    """Resolve um nome de tipo para seu tipo semântico"""
    if type_str in ['integer', 'real', 'boolean', 'string']:
        return type_str
    elif type_str.startswith('array'):
        try:
            range_part = type_str.split('[')[1].split(']')[0]
            base_type = type_str.split('of ')[1].strip()
            start, end = map(int, range_part.split('..'))
            return ArrayType(base_type, start, end)
        except:
            symbol_table.add_error(f"Erro ao analisar tipo de array: {type_str}", line_num)
            return None
    else:
        symbol_table.add_error(f"Tipo desconhecido: {type_str}", line_num)
        return None


def semantic_check_variable_declaration(id_list, type_str, symbol_table, line_num=None):
    """Verifica declaração de variáveis"""
    resolved_type = resolve_type(type_str, symbol_table, line_num)
    if resolved_type:
        for var_id in id_list.split(','):
            var_id = var_id.strip()
            if '[' in var_id:
                var_name = var_id.split('[')[0].strip()
                symbol_table.add_symbol(var_name, 'variable', resolved_type, None, line_num)
            else:
                symbol_table.add_symbol(var_id, 'variable', resolved_type, None, line_num)
    return resolved_type

def semantic_check_assignment(var_name, expr, symbol_table, line_num=None):
    """Verifica atribuição de valores"""
    var_symbol = symbol_table.verify_identifier(var_name, 'variable', line_num)
    if not var_symbol:
        return False
        
    expr_type = analyze_expression(expr, symbol_table, line_num)
    if not expr_type:
        return False
        
    result = symbol_table.check_types(var_symbol.data_type, expr_type, ':=', line_num)
    if result:
        var_symbol.initialized = True
        return True
    return False

def semantic_check_function_call(func_name, args, symbol_table, line_num=None):
    """Verifica chamada de função/procedimento"""
    func_symbol = symbol_table.verify_identifier(func_name, 'function_call', line_num)
    if not func_symbol:
        return None
        
    if len(args) != len(func_symbol.params):
        symbol_table.add_error(f"Número incorreto de argumentos para '{func_name}'", line_num)
        return None
        
    for i, arg in enumerate(args):
        arg_type = analyze_expression(arg, symbol_table, line_num)
        param_type = func_symbol.params[i].data_type
        symbol_table.check_types(param_type, arg_type, ':=', line_num)
        
    return func_symbol.data_type if func_symbol.kind == 'function' else None
