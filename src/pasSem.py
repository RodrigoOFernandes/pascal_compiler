import sys
from ASTNode import *

class Symbol:
    def __init__(self, name, type, is_array=False, array_size=None, is_function=False, is_procedure=False, params=None):
        self.name = name
        self.type = type
        self.is_array = is_array
        self.array_size = array_size
        self.is_function = is_function
        self.is_procedure = is_procedure
        self.params = params if params else []
    
    def __str__(self):
        if self.is_array:
            return f"Symbol(name={self.name}, type=Array of {self.type}, size={self.array_size})"
        elif self.is_function:
            params_str = ", ".join(str(p) for p in self.params)
            return f"Symbol(name={self.name}, type=Function returning {self.type}, params=[{params_str}])"
        elif self.is_procedure:
            params_str = ", ".join(str(p) for p in self.params)
            return f"Symbol(name={self.name}, type=Procedure, params=[{params_str}])"
        else:
            return f"Symbol(name={self.name}, type={self.type})"


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
    
    def add_symbol(self, symbol):
        if symbol.name in self.symbols:
            return False  # Symbol already exists in this scope
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None
    
    def __str__(self):
        result = "Symbol Table:\n"
        for name, symbol in self.symbols.items():
            result += f"  {symbol}\n"
        return result


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.errors = []
        self.current_function = None
        self.in_loop = False
    
    def analyze(self, ast):
        """Main entry point for semantic analysis."""
        if isinstance(ast, Program):
            self.visit_program(ast)
        
        return len(self.errors) == 0, self.errors
    
    def error(self, message, node=None):
        """Add an error message."""
        node_info = f" at {node.__class__.__name__}" if node else ""
        self.errors.append(f"Semantic Error{node_info}: {message}")
    
    def enter_scope(self):
        """Create a new scope."""
        self.current_scope = SymbolTable(self.current_scope)
    
    def exit_scope(self):
        """Exit the current scope."""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def visit_program(self, node):
        """Visit a Program node."""
        self.visit_block(node.block)
    
    def visit_block(self, node):
        """Visit a Block node."""
        if node.var_declaration_part:
            self.visit_var_declaration_part(node.var_declaration_part)
        
        if node.proc_or_func_declarations:
            for proc_or_func in node.proc_or_func_declarations:
                if isinstance(proc_or_func, ProcedureDeclaration):
                    self.visit_procedure_declaration(proc_or_func)
                elif isinstance(proc_or_func, FunctionDeclaration):
                    self.visit_function_declaration(proc_or_func)
        
        if hasattr(node, 'additional_var_declarations') and node.additional_var_declarations:
            self.visit_var_declaration_part(node.additional_var_declarations)
        
        if node.statement_part:
            self.visit_statement_part(node.statement_part)
    
    def visit_var_declaration_part(self, node):
        """Visit a VarDeclarationPart node."""
        if node.declarations:
            for decl in node.declarations:
                self.visit_var_declaration(decl)
    
    def visit_var_declaration(self, node):
        """Visit a VarDeclaration node."""
        type_info = self.get_type_info(node.type)
        
        for id_node in node.id_list:
            if isinstance(id_node, Identifier):
                symbol = Symbol(id_node.name, type_info)
                if not self.current_scope.add_symbol(symbol):
                    self.error(f"Variable '{id_node.name}' already defined in this scope", node)
            elif isinstance(id_node, ArrayId):
                # Handle array declaration
                symbol = Symbol(id_node.name, type_info, is_array=True, array_size=id_node.index)
                if not self.current_scope.add_symbol(symbol):
                    self.error(f"Array '{id_node.name}' already defined in this scope", node)
    
    def get_type_info(self, type_node):
        """Extract type information from a Type node."""
        if isinstance(type_node, Type):
            return type_node.name
        elif isinstance(type_node, ArrayType):
            return f"array of {self.get_type_info(type_node.element_type)}"
        return "unknown"
    
    def visit_procedure_declaration(self, node):
        """Visit a ProcedureDeclaration node."""
        proc_name = node.heading.name
        params = []
        
        if node.heading.parameters:
            for param in node.heading.parameters:
                param_type = self.get_type_info(param.type)
                params.append(Symbol(param.name, param_type))
        
        proc_symbol = Symbol(proc_name, None, is_procedure=True, params=params)
        if not self.current_scope.add_symbol(proc_symbol):
            self.error(f"Procedure '{proc_name}' already defined in this scope", node)
        
        self.enter_scope()
        
        if node.heading.parameters:
            for param in node.heading.parameters:
                param_type = self.get_type_info(param.type)
                param_symbol = Symbol(param.name, param_type)
                self.current_scope.add_symbol(param_symbol)
        
        self.visit_block(node.block)
        
        self.exit_scope()
    
    def visit_function_declaration(self, node):
        func_name = node.heading.name
        return_type = self.get_type_info(node.heading.return_type)
        params = []
        
        if node.heading.parameters:
            for param in node.heading.parameters:
                param_type = self.get_type_info(param.type)
                params.append(Symbol(param.name, param_type))
        
        func_symbol = Symbol(func_name, return_type, is_function=True, params=params)
        if not self.current_scope.add_symbol(func_symbol):
            self.error(f"Function '{func_name}' already defined in this scope", node)
        
        self.enter_scope()
        self.current_function = func_name
        
        if node.heading.parameters:
            for param in node.heading.parameters:
                param_type = self.get_type_info(param.type)
                param_symbol = Symbol(param.name, param_type)
                self.current_scope.add_symbol(param_symbol)

        self.current_scope.add_symbol(Symbol(func_name, return_type))
        
        self.visit_block(node.block)
        
        self.current_function = None
        self.exit_scope()
    
    def visit_statement_part(self, node):
        if node.statement_sequence:
            self.visit_statement_sequence(node.statement_sequence)
    
    def visit_statement_sequence(self, node):
        if node.statements:
            for stmt in node.statements:
                self.visit_statement(stmt)
    
    def visit_statement(self, node):
        if isinstance(node, Assignment):
            self.visit_assignment(node)
        elif isinstance(node, IfStatement):
            self.visit_if_statement(node)
        elif isinstance(node, WhileStatement):
            self.visit_while_statement(node)
        elif isinstance(node, RepeatStatement):
            self.visit_repeat_statement(node)
        elif isinstance(node, ForStatement):
            self.visit_for_statement(node)
        elif isinstance(node, ProcedureCall):
            self.visit_procedure_call(node)
        elif isinstance(node, WritelnStatement):
            self.visit_writeln_statement(node)
        elif isinstance(node, ReadlnStatement):
            self.visit_readln_statement(node)
        elif isinstance(node, BreakStatement):
            self.visit_break_statement(node)
        elif isinstance(node, ContinueStatement):
            self.visit_continue_statement(node)
        elif isinstance(node, CaseStatement):
            self.visit_case_statement(node)
        elif isinstance(node, StatementPart):
            self.visit_statement_part(node)
        elif isinstance(node, StatementSequence):
            self.visit_statement_sequence(node)
        elif isinstance(node, ArrayAssignment):
            self.visit_array_assignment(node)
    
    def visit_assignment(self, node):
        var_name = node.target.name
        var_symbol = self.current_scope.lookup(var_name)
        if not var_symbol:
            self.error(f"Undefined variable '{var_name}'", node)
            return
        
        if var_symbol.is_procedure:
            self.error(f"Cannot assign to procedure '{var_name}'", node)
            return
        
        expr_type = self.get_expression_type(node.expression)
        
        if expr_type and var_symbol.type and not self.are_types_compatible(expr_type, var_symbol.type):
            self.error(f"Type mismatch in assignment: cannot assign {expr_type} to {var_symbol.type}", node)
    
    def visit_array_assignment(self, node):
        array_name = node.array_name
        array_symbol = self.current_scope.lookup(array_name)
        
        if not array_symbol:
            self.error(f"Undefined array '{array_name}'", node)
            return
        
        if not array_symbol.is_array:
            self.error(f"Variable '{array_name}' is not an array", node)
            return
        
        index_type = self.get_expression_type(node.index)
        if index_type and index_type != "INTEGER":
            self.error(f"Array index must be an integer, got {index_type}", node)
        
        expr_type = self.get_expression_type(node.expression)
        base_type = array_symbol.type.replace("array of ", "")
        
        if expr_type and base_type and not self.are_types_compatible(expr_type, base_type):
            self.error(f"Type mismatch in array assignment: cannot assign {expr_type} to {base_type}", node)
    
    def visit_if_statement(self, node):
        cond_type = self.get_expression_type(node.condition)
        if cond_type and cond_type != "BOOLEAN":
            self.error(f"If condition must be a boolean, got {cond_type}", node)
        
        self.visit_statement(node.then_stmt)
        if node.else_stmt:
            self.visit_statement(node.else_stmt)
    
    def visit_while_statement(self, node):
        cond_type = self.get_expression_type(node.condition)
        if cond_type and cond_type != "BOOLEAN":
            self.error(f"While condition must be a boolean, got {cond_type}", node)
        
        old_in_loop = self.in_loop
        self.in_loop = True
        self.visit_statement(node.body)
        self.in_loop = old_in_loop
    
    def visit_repeat_statement(self, node):
        old_in_loop = self.in_loop
        self.in_loop = True
        self.visit_statement(node.body)
        
        # Check that the condition is a boolean
        cond_type = self.get_expression_type(node.condition)
        if cond_type and cond_type != "BOOLEAN":
            self.error(f"Repeat-until condition must be a boolean, got {cond_type}", node)
        
        self.in_loop = old_in_loop
    
    def visit_for_statement(self, node):
        """Visit a ForStatement node."""
        # Visit the initialization assignment
        self.visit_assignment(node.init)
        
        # Check the control variable (should be the same as in init)
        if isinstance(node.init, Assignment) and isinstance(node.init.target, Identifier):
            control_var = node.init.target.name
            control_var_symbol = self.current_scope.lookup(control_var)
            
            if control_var_symbol and control_var_symbol.type != "INTEGER":
                self.error(f"For loop control variable must be an integer, got {control_var_symbol.type}", node)
        
        # Check that the limit is an integer
        limit_type = self.get_expression_type(node.limit)
        if limit_type and limit_type != "INTEGER":
            self.error(f"For loop limit must be an integer, got {limit_type}", node)
        
        # Visit the loop body with loop context
        old_in_loop = self.in_loop
        self.in_loop = True
        self.visit_statement(node.body)
        self.in_loop = old_in_loop
    
    def visit_procedure_call(self, node):
        """Visit a ProcedureCall node."""
        proc_name = node.name
        proc_symbol = self.current_scope.lookup(proc_name)
        
        if not proc_symbol:
            self.error(f"Undefined procedure or function '{proc_name}'", node)
            return
        
        if not (proc_symbol.is_procedure or proc_symbol.is_function):
            self.error(f"'{proc_name}' is not a procedure or function", node)
            return
        
        # Check parameter count
        expected_params = proc_symbol.params
        actual_params = node.parameters if node.parameters else []
        
        if len(expected_params) != len(actual_params):
            self.error(f"Procedure '{proc_name}' expects {len(expected_params)} parameters, got {len(actual_params)}", node)
            return
        
        # Check parameter types
        for i, (expected, actual) in enumerate(zip(expected_params, actual_params)):
            actual_type = self.get_expression_type(actual)
            if actual_type and expected.type and not self.are_types_compatible(actual_type, expected.type):
                self.error(f"Type mismatch in parameter {i+1} of call to '{proc_name}': expected {expected.type}, got {actual_type}", node)
    
    def visit_writeln_statement(self, node):
        """Visit a WritelnStatement node."""
        if node.expressions:
            for expr in node.expressions:
                # All types can be written, but check that the expression is valid
                self.get_expression_type(expr)
    
    def visit_readln_statement(self, node):
        """Visit a ReadlnStatement node."""
        if node.variables:
            for var in node.variables:
                if isinstance(var, Identifier):
                    var_symbol = self.current_scope.lookup(var.name)
                    if not var_symbol:
                        self.error(f"Undefined variable '{var.name}' in readln", node)
                elif isinstance(var, ArrayId):
                    array_symbol = self.current_scope.lookup(var.name)
                    if not array_symbol:
                        self.error(f"Undefined array '{var.name}' in readln", node)
                    elif not array_symbol.is_array:
                        self.error(f"Variable '{var.name}' is not an array", node)
                    
                    # Check that the index is an integer
                    index_type = self.get_expression_type(var.index)
                    if index_type and index_type != "INTEGER":
                        self.error(f"Array index must be an integer, got {index_type}", node)
    
    def visit_break_statement(self, node):
        """Visit a BreakStatement node."""
        if not self.in_loop:
            self.error("Break statement outside of loop", node)
    
    def visit_continue_statement(self, node):
        """Visit a ContinueStatement node."""
        if not self.in_loop:
            self.error("Continue statement outside of loop", node)
    
    def visit_case_statement(self, node):
        """Visit a CaseStatement node."""
        # Check the expression type
        expr_type = self.get_expression_type(node.expression)
        
        if node.cases:
            for case in node.cases:
                # Check that the case value type matches the expression type
                case_type = self.get_expression_type(case.value)
                if expr_type and case_type and not self.are_types_compatible(expr_type, case_type):
                    self.error(f"Type mismatch in case: expression is {expr_type}, case value is {case_type}", node)
                
                # Visit the case statement
                self.visit_statement(case.statement)
    
    def get_expression_type(self, node):
        """Determine the type of an expression."""
        if isinstance(node, Literal):
            if node.literal_type == 'NUMBER':
                # Differentiate between INTEGER and REAL
                if isinstance(node.value, int) or (isinstance(node.value, str) and '.' not in node.value):
                    return "INTEGER"
                else:
                    return "REAL"
            elif node.literal_type == 'BOOL':
                return "BOOLEAN"
            elif node.literal_type == 'PHRASE':
                return "STRING"
        
        elif isinstance(node, Identifier):
            symbol = self.current_scope.lookup(node.name)
            if not symbol:
                self.error(f"Undefined identifier '{node.name}'", node)
                return None
            return symbol.type
        
        elif isinstance(node, ArrayId):
            symbol = self.current_scope.lookup(node.name)
            if not symbol:
                self.error(f"Undefined array '{node.name}'", node)
                return None
            
            if not symbol.is_array:
                self.error(f"Variable '{node.name}' is not an array", node)
                return None
            
            # Check that the index is an integer
            index_type = self.get_expression_type(node.index)
            if index_type and index_type != "INTEGER":
                self.error(f"Array index must be an integer, got {index_type}", node)
            
            # Return the base type of the array
            return symbol.type.replace("array of ", "")
        
        elif isinstance(node, BinaryOp):
            left_type = self.get_expression_type(node.left)
            right_type = self.get_expression_type(node.right)
            
            # Logical operators
            if node.op in ['AND', 'OR']:
                if left_type != "BOOLEAN" or right_type != "BOOLEAN":
                    self.error(f"Logical operator '{node.op}' requires boolean operands, got {left_type} and {right_type}", node)
                return "BOOLEAN"
            
            # Comparison operators
            elif node.op in ['EQUALS', 'DIFFERENT', 'LESSTHAN', 'LESSEQUAL', 'GREATERTHAN', 'GREATEREQUAL']:
                if not (left_type and right_type and self.are_types_compatible(left_type, right_type)):
                    self.error(f"Comparison operator '{node.op}' requires compatible types, got {left_type} and {right_type}", node)
                return "BOOLEAN"
            
            # Arithmetic operators
            elif node.op in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'DIV', 'MOD']:
                if left_type in ["INTEGER", "REAL"] and right_type in ["INTEGER", "REAL"]:
                    # Determine the result type
                    if left_type == "REAL" or right_type == "REAL" or node.op == 'DIVIDE':
                        return "REAL"
                    else:
                        return "INTEGER"
                else:
                    self.error(f"Arithmetic operator '{node.op}' requires numeric operands, got {left_type} and {right_type}", node)
                    return None
        
        elif isinstance(node, UnaryOp):
            expr_type = self.get_expression_type(node.expr)
            
            if node.op == 'NOT':
                if expr_type != "BOOLEAN":
                    self.error(f"Unary 'NOT' requires a boolean operand, got {expr_type}", node)
                return "BOOLEAN"
        
        elif isinstance(node, ProcedureCall):
            symbol = self.current_scope.lookup(node.name)
            if not symbol:
                self.error(f"Undefined procedure or function '{node.name}'", node)
                return None
            
            if not symbol.is_function:
                self.error(f"'{node.name}' is not a function and cannot be used in an expression", node)
                return None
            
            # Check parameters (same as in visit_procedure_call)
            expected_params = symbol.params
            actual_params = node.parameters if node.parameters else []
            
            if len(expected_params) != len(actual_params):
                self.error(f"Function '{node.name}' expects {len(expected_params)} parameters, got {len(actual_params)}", node)
            else:
                for i, (expected, actual) in enumerate(zip(expected_params, actual_params)):
                    actual_type = self.get_expression_type(actual)
                    if actual_type and expected.type and not self.are_types_compatible(actual_type, expected.type):
                        self.error(f"Type mismatch in parameter {i+1} of call to '{node.name}': expected {expected.type}, got {actual_type}", node)
            
            return symbol.type
        
        elif isinstance(node, LengthFunction):
            expr_type = self.get_expression_type(node.expression)
            if expr_type != "STRING" and not (expr_type and "array" in expr_type):
                self.error(f"Length function requires a string or array operand, got {expr_type}", node)
            return "INTEGER"
        
        return None
    
    def are_types_compatible(self, type1, type2):
        """Check if two types are compatible for assignment or comparison."""
        if type1 == type2:
            return True
        
        # Special case for INTEGER and REAL
        if (type1 == "INTEGER" and type2 == "REAL") or (type1 == "REAL" and type2 == "INTEGER"):
            return True
        
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python PasSemanticAnalyzer.py <ast_object>")
        sys.exit(1)
    
    ast = sys.argv[1]  # This would be the AST object in a real implementation
    analyzer = SemanticAnalyzer()
    success, errors = analyzer.analyze(ast)
    
    if success:
        print("Semantic analysis completed successfully!")
    else:
        print("Semantic analysis failed with the following errors:")
        for error in errors:
            print(f"- {error}")


if __name__ == "__main__":
    main()
