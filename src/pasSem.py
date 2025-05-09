from ASTNode import *

class Symbol:
    def __init__(self, name, type_name, is_initialized=False, is_constant=False, value=None):
        self.name = name
        self.type_name = type_name  # 'INTEGER', 'REAL', 'BOOLEAN', 'STRING', or array type
        self.is_initialized = is_initialized
        self.is_constant = is_constant
        self.value = value  # For constants

    def __str__(self):
        init_status = "initialized" if self.is_initialized else "uninitialized"
        const_status = "constant" if self.is_constant else "variable"
        return f"Symbol({self.name}, {self.type_name}, {init_status}, {const_status})"


class ProcedureSymbol(Symbol):
    def __init__(self, name, params=None, return_type=None):
        super().__init__(name, return_type if return_type else "PROCEDURE")
        self.params = params or []  # List of Parameter symbols
        self.is_function = return_type is not None

    def __str__(self):
        type_str = "function" if self.is_function else "procedure"
        return f"{type_str} {self.name}({', '.join(str(p) for p in self.params)})"


class ArraySymbol(Symbol):
    def __init__(self, name, element_type, dimensions=None):
        super().__init__(name, "ARRAY")
        self.element_type = element_type  # The type of elements stored in the array
        self.dimensions = dimensions or []  # List of (start, end) tuples for each dimension

    def __str__(self):
        dims = ", ".join([f"{start}..{end}" for start, end in self.dimensions])
        return f"ArraySymbol({self.name}, {self.element_type}, [{dims}])"


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}  # Dictionary to store symbols: name -> Symbol
        self.parent = parent  # Parent scope (for nested scopes)

    def define(self, symbol):
        """Add a symbol to the current scope."""
        self.symbols[symbol.name] = symbol
        return symbol

    def lookup(self, name, current_scope_only=False):
        """Look up a symbol in this scope or parent scopes."""
        if name in self.symbols:
            return self.symbols[name]
        
        if not current_scope_only and self.parent:
            return self.parent.lookup(name)
        
        return None


class SemanticError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ASTSemanticAnalyzer:
    def __init__(self):
        self.current_scope = None
        self.errors = []
        self.loop_level = 0  # To track if break/continue are inside loops
        self.standard_procedures = {
            "writeln": ProcedureSymbol("writeln"),
            "write": ProcedureSymbol("write"),
            "readln": ProcedureSymbol("readln"),
            "read": ProcedureSymbol("read")
        }
        self.standard_functions = {
            "length": ProcedureSymbol("length", [], "INTEGER")
        }
        
        # Type compatibility matrix - updated for better literal handling
        self.type_compatibility = {
            "INTEGER": {"INTEGER": "INTEGER", "REAL": "REAL", "NUMBER": "INTEGER"},
            "REAL": {"INTEGER": "REAL", "REAL": "REAL", "NUMBER": "REAL"},
            "BOOLEAN": {"BOOLEAN": "BOOLEAN"},
            "STRING": {"STRING": "STRING", "PHRASE": "STRING"},
            "CHAR": {"CHAR": "CHAR", "STRING": "STRING", "PHRASE": "STRING"}  # Novo tipo
        }
        
        # Operator type checking rules - updated for literals
        self.operator_rules = {
            "+": {
                ("INTEGER", "INTEGER"): "INTEGER",
                ("REAL", "REAL"): "REAL",
                ("INTEGER", "REAL"): "REAL",
                ("REAL", "INTEGER"): "REAL",
                ("STRING", "STRING"): "STRING",
                ("INTEGER", "NUMBER"): "INTEGER",
                ("NUMBER", "INTEGER"): "INTEGER",
                ("NUMBER", "NUMBER"): "NUMBER",
                ("PHRASE", "PHRASE"): "STRING"
            },
            "-": {
                ("INTEGER", "INTEGER"): "INTEGER",
                ("REAL", "REAL"): "REAL",
                ("INTEGER", "REAL"): "REAL",
                ("REAL", "INTEGER"): "REAL",
                ("INTEGER", "NUMBER"): "INTEGER",
                ("NUMBER", "INTEGER"): "INTEGER",
                ("NUMBER", "NUMBER"): "NUMBER"
            },
            "*": {
                ("INTEGER", "INTEGER"): "INTEGER",
                ("REAL", "REAL"): "REAL",
                ("INTEGER", "REAL"): "REAL",
                ("REAL", "INTEGER"): "REAL",
                ("INTEGER", "NUMBER"): "INTEGER",
                ("NUMBER", "INTEGER"): "INTEGER",
                ("NUMBER", "NUMBER"): "NUMBER"
            },
            "/": {
                ("INTEGER", "INTEGER"): "REAL",
                ("REAL", "REAL"): "REAL",
                ("INTEGER", "REAL"): "REAL",
                ("REAL", "INTEGER"): "REAL",
                ("INTEGER", "NUMBER"): "REAL",
                ("NUMBER", "INTEGER"): "REAL",
                ("NUMBER", "NUMBER"): "REAL"
            },
            "DIV": {
                ("INTEGER", "INTEGER"): "INTEGER",
                ("INTEGER", "NUMBER"): "INTEGER",
                ("NUMBER", "INTEGER"): "INTEGER",
                ("NUMBER", "NUMBER"): "INTEGER"
            },
            "MOD": {
                ("INTEGER", "INTEGER"): "INTEGER",
                ("INTEGER", "NUMBER"): "INTEGER",
                ("NUMBER", "INTEGER"): "INTEGER",
                ("NUMBER", "NUMBER"): "INTEGER"
            },
            "=": {
                ("INTEGER", "INTEGER"): "BOOLEAN",
                ("REAL", "REAL"): "BOOLEAN",
                ("INTEGER", "REAL"): "BOOLEAN",
                ("REAL", "INTEGER"): "BOOLEAN",
                ("BOOLEAN", "BOOLEAN"): "BOOLEAN",
                ("STRING", "STRING"): "BOOLEAN",
                ("INTEGER", "NUMBER"): "BOOLEAN",
                ("NUMBER", "INTEGER"): "BOOLEAN",
                ("NUMBER", "NUMBER"): "BOOLEAN",
                ("STRING", "PHRASE"): "BOOLEAN",
                ("PHRASE", "STRING"): "BOOLEAN",
                ("PHRASE", "PHRASE"): "BOOLEAN",                
                ("CHAR", "CHAR"): "BOOLEAN",
                ("CHAR", "STRING"): "BOOLEAN",
                ("STRING", "CHAR"): "BOOLEAN",
                ("CHAR", "PHRASE"): "BOOLEAN",
                ("PHRASE", "CHAR"): "BOOLEAN"
                },
            "<>": {
                ("INTEGER", "INTEGER"): "BOOLEAN",
                ("REAL", "REAL"): "BOOLEAN",
                ("INTEGER", "REAL"): "BOOLEAN",
                ("REAL", "INTEGER"): "BOOLEAN",
                ("BOOLEAN", "BOOLEAN"): "BOOLEAN",
                ("STRING", "STRING"): "BOOLEAN",
                ("INTEGER", "NUMBER"): "BOOLEAN",
                ("NUMBER", "INTEGER"): "BOOLEAN",
                ("NUMBER", "NUMBER"): "BOOLEAN",
                ("STRING", "PHRASE"): "BOOLEAN",
                ("PHRASE", "STRING"): "BOOLEAN",
                ("PHRASE", "PHRASE"): "BOOLEAN"
            },
            "<": {
                ("INTEGER", "INTEGER"): "BOOLEAN",
                ("REAL", "REAL"): "BOOLEAN",
                ("INTEGER", "REAL"): "BOOLEAN",
                ("REAL", "INTEGER"): "BOOLEAN",
                ("STRING", "STRING"): "BOOLEAN",
                ("INTEGER", "NUMBER"): "BOOLEAN",
                ("NUMBER", "INTEGER"): "BOOLEAN",
                ("NUMBER", "NUMBER"): "BOOLEAN",
                ("STRING", "PHRASE"): "BOOLEAN",
                ("PHRASE", "STRING"): "BOOLEAN",
                ("PHRASE", "PHRASE"): "BOOLEAN"
            },
            "<=": {
                ("INTEGER", "INTEGER"): "BOOLEAN",
                ("REAL", "REAL"): "BOOLEAN",
                ("INTEGER", "REAL"): "BOOLEAN",
                ("REAL", "INTEGER"): "BOOLEAN",
                ("STRING", "STRING"): "BOOLEAN",
                ("INTEGER", "NUMBER"): "BOOLEAN",
                ("NUMBER", "INTEGER"): "BOOLEAN",
                ("NUMBER", "NUMBER"): "BOOLEAN",
                ("STRING", "PHRASE"): "BOOLEAN",
                ("PHRASE", "STRING"): "BOOLEAN",
                ("PHRASE", "PHRASE"): "BOOLEAN"
            },
            ">": {
                ("INTEGER", "INTEGER"): "BOOLEAN",
                ("REAL", "REAL"): "BOOLEAN",
                ("INTEGER", "REAL"): "BOOLEAN",
                ("REAL", "INTEGER"): "BOOLEAN",
                ("STRING", "STRING"): "BOOLEAN",
                ("INTEGER", "NUMBER"): "BOOLEAN",
                ("NUMBER", "INTEGER"): "BOOLEAN",
                ("NUMBER", "NUMBER"): "BOOLEAN",
                ("STRING", "PHRASE"): "BOOLEAN",
                ("PHRASE", "STRING"): "BOOLEAN",
                ("PHRASE", "PHRASE"): "BOOLEAN"
            },
            ">=": {
                ("INTEGER", "INTEGER"): "BOOLEAN",
                ("REAL", "REAL"): "BOOLEAN",
                ("INTEGER", "REAL"): "BOOLEAN",
                ("REAL", "INTEGER"): "BOOLEAN",
                ("STRING", "STRING"): "BOOLEAN",
                ("INTEGER", "NUMBER"): "BOOLEAN",
                ("NUMBER", "INTEGER"): "BOOLEAN",
                ("NUMBER", "NUMBER"): "BOOLEAN",
                ("STRING", "PHRASE"): "BOOLEAN",
                ("PHRASE", "STRING"): "BOOLEAN",
                ("PHRASE", "PHRASE"): "BOOLEAN"
            },
            "AND": {
                ("BOOLEAN", "BOOLEAN"): "BOOLEAN"
            },
            "OR": {
                ("BOOLEAN", "BOOLEAN"): "BOOLEAN"
            }
        }
        
        # Unary operator rules - updated for literals
        self.unary_operator_rules = {
            "NOT": {
                "BOOLEAN": "BOOLEAN"
            },
            "-": {
                "INTEGER": "INTEGER",
                "REAL": "REAL",
                "NUMBER": "NUMBER"
            }
        }

    def error(self, message):
        """Add a semantic error to the list of errors."""
        self.errors.append(message)
        print(f"Semantic Error: {message}")

    def analyze(self, ast):
        """Analyze the AST for semantic errors."""
        self.current_scope = SymbolTable()  # Global scope
        
        # Add built-in functions and procedures
        for name, proc in self.standard_procedures.items():
            self.current_scope.define(proc)
        
        for name, func in self.standard_functions.items():
            self.current_scope.define(func)
        
        # Start analyzing from the root node
        self.visit(ast)
        
        if self.errors:
            print(f"Found {len(self.errors)} semantic errors:")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
            return False
        else:
            print("No semantic errors found.")
            return True

    def visit(self, node):
        """Visit a node in the AST."""
        if node is None:
            return None
        
        # Use reflection to call the appropriate visit method
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Default visitor method for unknown node types."""
        print(f"Warning: No visitor method defined for {node.__class__.__name__}")
        return None

    def visit_Program(self, node):
        self.visit(node.header)
        self.visit(node.block)
        return None

    def visit_Header(self, node):
        # Nothing to check in the header
        return None

    def visit_Block(self, node):
        # Create a new scope for this block
        old_scope = self.current_scope
        self.current_scope = SymbolTable(old_scope)
        
        # Process variable declarations
        if node.var_decl_part:
            self.visit(node.var_decl_part)
        
        # Process procedure and function declarations
        if hasattr(node, "proc_func_part") and node.proc_func_part:
            for proc_or_func in node.proc_func_part:
                self.visit(proc_or_func)
        
        # Process additional variable declarations after procedures
        if hasattr(node, "extra_var_decl") and node.extra_var_decl:
            self.visit(node.extra_var_decl)
        
        # Process statements
        if node.statement_part:
            self.visit(node.statement_part)
        
        # Restore the previous scope
        self.current_scope = old_scope
        return None

    def visit_VarDeclarationPart(self, node):
        if hasattr(node, "declarations") and node.declarations:
            for decl in node.declarations:
                self.visit(decl)
        return None

    def visit_VarDeclaration(self, node):
        # Get the type object
        type_info = self.visit(node.type_name)
        
        for id_node in node.id_list:
            if isinstance(id_node, Identifier):
                # Check if variable is already declared in current scope
                if self.current_scope.lookup(id_node.name, True):
                    self.error(f"Variable {id_node.name} already declared in this scope")
                
                # Register the variable in the symbol table
                if isinstance(type_info, str):  # Basic type
                    symbol = Symbol(id_node.name, type_info)
                    self.current_scope.define(symbol)
                elif isinstance(type_info, tuple) and type_info[0] == "ARRAY":
                    # For array types
                    element_type, dimensions = type_info[1], type_info[2]
                    array_symbol = ArraySymbol(id_node.name, element_type, dimensions)
                    self.current_scope.define(array_symbol)
            elif isinstance(id_node, ArrayId):
                self.error(f"Cannot declare array with index in declaration: {id_node.id_name}")
        
        return None

    def visit_Type(self, node):
        # Normalize type names to uppercase for consistency
        type_name = node.type_name.upper()
        if type_name in ["INTEGER", "REAL", "BOOLEAN", "STRING"]:
            return type_name
        else:
            self.error(f"Unknown type: {node.type_name}")
            return "UNKNOWN"

    def visit_ArrayType(self, node):
        # Get the element type
        element_type = self.visit(node.element_type)
        
        # Get the range information
        dimensions = []
        if hasattr(node, "range") and node.range:
            range_info = self.visit(node.range)
            if range_info:
                dimensions.append(range_info)
        
        return ("ARRAY", element_type, dimensions)

    def visit_Range(self, node):
        start_type = self.visit(node.start)
        end_type = self.visit(node.end)
        
        # Allow NUMBER literals in range expressions
        valid_start = start_type == "INTEGER" or start_type == "NUMBER"
        valid_end = end_type == "INTEGER" or end_type == "NUMBER"
        
        if not valid_start or not valid_end:
            self.error(f"Array range must be of INTEGER type, got {start_type} and {end_type}")
            return None
        
        # If we have literal values, we can check the range
        if isinstance(node.start, Literal) and isinstance(node.end, Literal):
            start_val = int(node.start.value) if isinstance(node.start.value, (int, float)) else 0
            end_val = int(node.end.value) if isinstance(node.end.value, (int, float)) else 0
            
            if start_val > end_val:
                self.error(f"Invalid array range: {start_val}..{end_val}")
                return None
            
            return (start_val, end_val)
        
        return (0, 0)  # Default range if we can't determine at compile time

    def visit_Identifier(self, node):
        # Look up the identifier in the symbol table
        symbol = self.current_scope.lookup(node.name)
        
        if not symbol:
            self.error(f"Undeclared identifier: {node.name}")
            return "UNKNOWN"
        
        return symbol.type_name

    def visit_ArrayId(self, node):
        # Look up the array identifier
        symbol = self.current_scope.lookup(node.id_name)
        
        if not symbol:
            self.error(f"Undeclared array: {node.id_name}")
            return "UNKNOWN"
        
        # Modificação aqui: Permitir acesso a strings como arrays
        if isinstance(symbol, ArraySymbol):
            # Caso normal para arrays
            pass  # Manter o código existente
        elif symbol.type_name == "STRING":
            # Nova verificação para strings como arrays de caracteres
            # Check that the index expression is of integer type
            index_type = self.visit(node.expression)
            if index_type != "INTEGER" and index_type != "NUMBER":
                self.error(f"String index must be an integer, got {index_type}")
            
            # Return CHAR as the element type for strings
            return "CHAR"  # Ou poderia retornar "STRING" se preferirem
        else:
            self.error(f"{node.id_name} is not an array or string")
            return "UNKNOWN"
        
        # Check that the index expression is of integer type
        index_type = self.visit(node.expression)
        if index_type != "INTEGER" and index_type != "NUMBER":
            self.error(f"Array index must be an integer, got {index_type}")
        
        # Return the element type of the array
        return symbol.element_type

    def visit_ProcedureDeclaration(self, node):
        # Visit the procedure heading
        proc_symbol = self.visit(node.heading)
        
        # Create a new scope for the procedure body
        old_scope = self.current_scope
        proc_scope = SymbolTable(old_scope)
        self.current_scope = proc_scope
        
        # Add parameters to the procedure scope
        for param in proc_symbol.params:
            self.current_scope.define(param)
        
        # Visit the procedure body
        self.visit(node.block)
        
        # Restore the previous scope
        self.current_scope = old_scope
        return None

    def visit_FunctionDeclaration(self, node):
        # Visit the function heading
        func_symbol = self.visit(node.heading)
        
        # Create a new scope for the function body
        old_scope = self.current_scope
        func_scope = SymbolTable(old_scope)
        self.current_scope = func_scope
        
        # Add parameters to the function scope
        for param in func_symbol.params:
            self.current_scope.define(param)
        
        # Add a special result variable for the function return value
        result_symbol = Symbol(func_symbol.name, func_symbol.type_name)
        self.current_scope.define(result_symbol)
        
        # Visit the function body
        self.visit(node.block)
        
        # Check if the function result was assigned
        if not self.current_scope.lookup(func_symbol.name).is_initialized:
            self.error(f"Function {func_symbol.name} does not have a return value")
        
        # Restore the previous scope
        self.current_scope = old_scope
        return None

    def visit_ProcedureHeading(self, node):
        # Check if procedure is already declared
        if self.current_scope.lookup(node.name, True):
            self.error(f"Procedure {node.name} already declared in this scope")
        
        # Process parameters
        params = []
        if hasattr(node, "params") and node.params:
            for param in node.params:
                param_symbol = self.visit(param)
                params.append(param_symbol)
        
        # Create and register the procedure symbol
        proc_symbol = ProcedureSymbol(node.name, params)
        self.current_scope.define(proc_symbol)
        
        return proc_symbol

    def visit_FunctionHeading(self, node):
        # Check if function is already declared
        if self.current_scope.lookup(node.name, True):
            self.error(f"Function {node.name} already declared in this scope")
        
        # Get return type
        return_type = self.visit(node.return_type) if node.return_type else None
        
        # Process parameters
        params = []
        if hasattr(node, "params") and node.params:
            for param in node.params:
                param_symbol = self.visit(param)
                params.append(param_symbol)
        
        # Create and register the function symbol
        func_symbol = ProcedureSymbol(node.name, params, return_type)
        self.current_scope.define(func_symbol)
        
        return func_symbol

    def visit_Parameter(self, node):
        # Get parameter type
        param_type = self.visit(node.type_name)
        
        # Create a symbol for the parameter
        param_symbol = Symbol(node.name, param_type, True)  # Parameters are considered initialized
        return param_symbol

    def visit_StatementPart(self, node):
        return self.visit(node.statement_sequence)

    def visit_StatementSequence(self, node):
        for stmt in node.statements:
            self.visit(stmt)
        return None

    def visit_Assignment(self, node):
        # Check that the target is a valid variable
        if isinstance(node.target, Identifier):
            target_symbol = self.current_scope.lookup(node.target.name)
            
            if not target_symbol:
                self.error(f"Undeclared variable: {node.target.name}")
                return None
            
            if target_symbol.is_constant:
                self.error(f"Cannot assign to constant: {node.target.name}")
                return None
            
            # Get the value type
            value_type = self.visit(node.value)
            
            # MODIFICAÇÃO: melhor tratamento para chamadas de função (ProcedureCall)
            # Se o valor é None, mas estamos lidando com uma chamada de procedimento que na verdade é uma função
            if value_type is None and isinstance(node.value, ProcedureCall):
                # Tentar novamente obtendo o símbolo da função
                proc_symbol = self.current_scope.lookup(node.value.procedure_name)
                if proc_symbol and isinstance(proc_symbol, ProcedureSymbol) and proc_symbol.is_function:
                    value_type = proc_symbol.type_name
            
            # Type checking
            if not self.check_type_compatibility(target_symbol.type_name, value_type):
                self.error(f"Type mismatch in assignment: cannot assign {value_type} to {target_symbol.type_name}")
                return None
            
            # Mark the variable as initialized
            target_symbol.is_initialized = True
        elif isinstance(node.target, ArrayId):
            # Handle array element assignment
            array_type = self.visit(node.target)
            value_type = self.visit(node.value)
            
            if not self.check_type_compatibility(array_type, value_type):
                self.error(f"Type mismatch in array assignment: cannot assign {value_type} to element of type {array_type}")
        else:
            # Handle other types of assignments
            self.error(f"Invalid assignment target: {node.target}")
        
        return None

    def visit_IfStatement(self, node):
        # Check that the condition is a boolean
        condition_type = self.visit(node.condition)
        
        if condition_type != "BOOLEAN":
            self.error(f"Condition in if statement must be of boolean type, got {condition_type}")
        
        # Visit the then branch
        self.visit(node.then_branch)
        
        # Visit the else branch if it exists
        if hasattr(node, "else_branch") and node.else_branch:
            self.visit(node.else_branch)
        
        return None

    def visit_WhileStatement(self, node):
        # Check that the condition is a boolean
        condition_type = self.visit(node.condition)
        
        if condition_type != "BOOLEAN":
            self.error(f"Condition in while statement must be of boolean type, got {condition_type}")
        
        # Enter a loop context for break/continue
        self.loop_level += 1
        
        # Visit the loop body
        self.visit(node.body)
        
        # Exit the loop context
        self.loop_level -= 1
        
        return None

    def visit_RepeatStatement(self, node):
        # Enter a loop context for break/continue
        self.loop_level += 1
        
        # Visit the loop body
        self.visit(node.body)
        
        # Check that the condition is a boolean
        condition_type = self.visit(node.condition)
        
        if condition_type != "BOOLEAN":
            self.error(f"Condition in repeat statement must be of boolean type, got {condition_type}")
        
        # Exit the loop context
        self.loop_level -= 1
        
        return None

    def visit_ForStatement(self, node):
        # Check the initialization assignment
        self.visit(node.init)
        
        # Make sure the control variable is an integer
        if isinstance(node.init, Assignment) and isinstance(node.init.target, Identifier):
            control_var = self.current_scope.lookup(node.init.target.name)
            
            if control_var and control_var.type_name != "INTEGER":
                self.error(f"For loop control variable must be of integer type, got {control_var.type_name}")
        
        # Check the limit expression is an integer
        limit_type = self.visit(node.limit)
        if limit_type != "INTEGER" and limit_type != "NUMBER":
            self.error(f"For loop limit must be of integer type, got {limit_type}")
        
        # Enter a loop context for break/continue
        self.loop_level += 1
        
        # Visit the loop body
        self.visit(node.body)
        
        # Exit the loop context
        self.loop_level -= 1
        
        return None

    def visit_ProcedureCall(self, node):
        # Look up the procedure
        proc_symbol = self.current_scope.lookup(node.procedure_name)
        
        if not proc_symbol:
            # Check if it's a standard procedure
            proc_symbol = self.standard_procedures.get(node.procedure_name)
            
            if not proc_symbol:
                self.error(f"Undeclared procedure: {node.procedure_name}")
                return None
        
        # MODIFICAÇÃO: permitir chamadas de função como procedimento quando o valor é descartado
        # Isso corrige o erro "BinToInt is not a procedure"
        if isinstance(proc_symbol, ProcedureSymbol):
            if proc_symbol.is_function:
                # É uma função, mas está sendo usada como procedimento
                # Em Pascal, isso é permitido quando o valor de retorno não é utilizado
                pass  # Removemos a mensagem de erro aqui
        else:
            self.error(f"{node.procedure_name} is not a procedure or function")
            return None
        
        # Special handling for standard procedures like writeln and readln
        if node.procedure_name.lower() in ["writeln", "write", "readln", "read"]:
            # These can take any number of parameters
            for param in node.params:
                param_type = self.visit(param)
                
                # For read/readln, make sure parameters are variables
                if node.procedure_name.lower() in ["readln", "read"]:
                    if isinstance(param, Identifier):
                        symbol = self.current_scope.lookup(param.name)
                        if symbol:
                            symbol.is_initialized = True
                    elif isinstance(param, ArrayId):
                        # Mark array element as accessed for read operation
                        pass
                    else:
                        self.error(f"Invalid target for read operation: {param}")
        else:
            # Normal procedure call with parameter type checking
            # Check parameter count
            if len(proc_symbol.params) != len(node.params):
                self.error(f"Procedure {node.procedure_name} expects {len(proc_symbol.params)} parameters, got {len(node.params)}")
                return None
            
            # Check parameter types
            for i, (param, arg) in enumerate(zip(proc_symbol.params, node.params)):
                arg_type = self.visit(arg)
                if not self.check_type_compatibility(param.type_name, arg_type):
                    self.error(f"Type mismatch in parameter {i+1} of procedure {node.procedure_name}: expected {param.type_name}, got {arg_type}")
        
        # MODIFICAÇÃO: retornar o tipo da função quando estamos tratando de uma função
        # Isso corrige o erro "Type mismatch in assignment: cannot assign None to INTEGER"
        if isinstance(proc_symbol, ProcedureSymbol) and proc_symbol.is_function:
            return proc_symbol.type_name
        
        return None

    def visit_WritelnStatement(self, node):
        # Writeln can take any expression type - check each one
        if hasattr(node, "params") and node.params:
            for param in node.params:
                param_type = self.visit(param)
        return None

    def visit_ReadlnStatement(self, node):
        # Check that each parameter is a variable that can be read into
        if hasattr(node, "params") and node.params:
            for param in node.params:
                if isinstance(param, Identifier):
                    symbol = self.current_scope.lookup(param.name)
                    
                    if not symbol:
                        self.error(f"Undeclared variable: {param.name}")
                    elif symbol.type_name not in ["INTEGER", "REAL", "STRING"]:
                        self.error(f"Cannot read into variable of type {symbol.type_name}")
                    else:
                        # Mark the variable as initialized
                        symbol.is_initialized = True
                elif isinstance(param, ArrayId):
                    # Get the array element type
                    element_type = self.visit(param)
                    if element_type not in ["INTEGER", "REAL", "STRING"]:
                        self.error(f"Cannot read into array element of type {element_type}")
                else:
                    self.error(f"Invalid target for read operation: {param}")
        
        return None

    def visit_BreakStatement(self, node):
        if self.loop_level == 0:
            self.error("Break statement must be inside a loop")
        return None

    def visit_ContinueStatement(self, node):
        if self.loop_level == 0:
            self.error("Continue statement must be inside a loop")
        return None

    def visit_CaseStatement(self, node):
        # Check the expression type
        expr_type = self.visit(node.expression)
        
        # All case values must be the same type as the expression
        for option in node.case_list:
            value_type = self.visit(option.value)
            
            if not self.check_type_compatibility(expr_type, value_type):
                self.error(f"Type mismatch in case option: expression is {expr_type}, but case value is {value_type}")
            
            # Visit the case statement
            self.visit(option.statement)
        
        return None

    def visit_BinaryOp(self, node):
        # Get the types of the operands
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        # Check if the operator is valid for these types
        if (left_type, right_type) in self.operator_rules.get(node.operator, {}):
            return self.operator_rules[node.operator][(left_type, right_type)]
        else:
            self.error(f"Invalid operands {left_type} and {right_type} for operator {node.operator}")
            return "UNKNOWN"

    def visit_UnaryOp(self, node):
        # Get the type of the operand
        operand_type = self.visit(node.operand)
        
        # Check if the operator is valid for this type
        if operand_type in self.unary_operator_rules.get(node.operator, {}):
            return self.unary_operator_rules[node.operator][operand_type]
        else:
            self.error(f"Invalid operand {operand_type} for unary operator {node.operator}")
            return "UNKNOWN"

    def visit_Literal(self, node):
        # Return the type based on the literal type
        return node.type_name

    def visit_FunctionCall(self, node):
        # Look up the function
        func_symbol = self.current_scope.lookup(node.function_name)
        
        if not func_symbol:
            # Check if it's a standard function
            func_symbol = self.standard_functions.get(node.function_name)
            
            if not func_symbol:
                self.error(f"Undeclared function: {node.function_name}")
                return "UNKNOWN"
        
        if not isinstance(func_symbol, ProcedureSymbol) or not func_symbol.is_function:
            self.error(f"{node.function_name} is not a function")
            return "UNKNOWN"
        
        # Special handling for built-in functions like length
        if node.function_name.lower() == "length":
            if len(node.params) != 1:
                self.error(f"Function length expects 1 parameter, got {len(node.params)}")
                return "INTEGER"
            
            param_type = self.visit(node.params[0])
            if param_type != "STRING":
                self.error(f"Function length expects a STRING parameter, got {param_type}")
            
            return "INTEGER"
        else:
            # Normal function call with parameter type checking
            # Check parameter count
            if len(func_symbol.params) != len(node.params):
                self.error(f"Function {node.function_name} expects {len(func_symbol.params)} parameters, got {len(node.params)}")
                return func_symbol.type_name
            
            # Check parameter types
            for i, (param, arg) in enumerate(zip(func_symbol.params, node.params)):
                arg_type = self.visit(arg)
                if not self.check_type_compatibility(param.type_name, arg_type):
                    self.error(f"Type mismatch in parameter {i+1} of function {node.function_name}: expected {param.type_name}, got {arg_type}")
            
            return func_symbol.type_name

    def visit_LengthFunction(self, node):
        # Check the parameter type
        expr_type = self.visit(node.expression)
        
        if expr_type != "STRING":
            self.error(f"Length function expects a STRING parameter, got {expr_type}")
        
        return "INTEGER"

    def visit_CaseOption(self, node):
        # Visit the case value
        value_type = self.visit(node.value)
        
        # Visit the case statement
        self.visit(node.statement)
        
        return value_type

    def check_type_compatibility(self, target_type, source_type):
        """Check if source_type can be assigned to target_type."""
        # Handle special case for NUMBER literals being assignable to INTEGER or REAL
        if source_type == "NUMBER":
            if target_type in ["INTEGER", "REAL"]:
                return True
        
        # Handle special case for PHRASE literals being assignable to STRING
        if source_type == "PHRASE" and target_type == "STRING":
            return True
        
        # Check the type compatibility matrix
        if target_type in self.type_compatibility:
            return source_type in self.type_compatibility[target_type]
        
        # For array assignments
        if target_type.startswith("ARRAY") and source_type.startswith("ARRAY"):
            # Would need more sophisticated checking for array dimensions
            return True
        return target_type == source_type
