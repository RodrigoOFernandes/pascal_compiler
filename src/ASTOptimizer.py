from ASTNode import *
class ASTOptimizer:
    def optimize(self, node):
        if node is None:
            return None
        
        method_name = f'optimize_{node.__class__.__name__}'
        optimizer = getattr(self, method_name, self.generic_optimize)
        return optimizer(node)
    
    def generic_optimize(self, node):
        return node
    
    def optimize_Program(self, node):
        node.header = self.optimize(node.header)
        node.block = self.optimize(node.block)
        return node
    
    def optimize_Header(self, node):
        return node
    
    def optimize_Block(self, node):
        node.var_decl_part = self.optimize(node.var_decl_part)
        
        if hasattr(node, "proc_func_part") and node.proc_func_part:
            optimized_procs = []
            for proc_or_func in node.proc_func_part:
                optimized_procs.append(self.optimize(proc_or_func))
            node.proc_func_part = optimized_procs
        
        if hasattr(node, "extra_var_decl") and node.extra_var_decl:
            node.extra_var_decl = self.optimize(node.extra_var_decl)
        
        node.statement_part = self.optimize(node.statement_part)
        return node
    
    def optimize_VarDeclarationPart(self, node):
        if hasattr(node, "declarations") and node.declarations:
            optimized_declarations = []
            for decl in node.declarations:
                optimized_declarations.append(self.optimize(decl))
            node.declarations = optimized_declarations
        return node
    
    def optimize_VarDeclaration(self, node):
        optimized_id_list = []
        for id_node in node.id_list:
            optimized_id_list.append(self.optimize(id_node))
        node.id_list = optimized_id_list
        
        node.type_name = self.optimize(node.type_name)  
        return node
    
    def optimize_Type(self, node):
        return node
    
    def optimize_ArrayType(self, node):
        if hasattr(node, "range"):
            node.range = self.optimize(node.range)
        node.element_type = self.optimize(node.element_type)
        return node
    
    def optimize_Identifier(self, node):
        return node
    
    def optimize_ArrayId(self, node):
        node.expression = self.optimize(node.expression)
        return node
    
    def optimize_ProcedureDeclaration(self, node):
        node.heading = self.optimize(node.heading)
        node.block = self.optimize(node.block)
        return node
    
    def optimize_FunctionDeclaration(self, node):
        node.heading = self.optimize(node.heading)
        node.block = self.optimize(node.block)
        return node
    
    def optimize_ProcedureHeading(self, node):
        if hasattr(node, "params") and node.params:
            optimized_params = []
            for param in node.params:
                optimized_params.append(self.optimize(param))
            node.params = optimized_params
        return node
    
    def optimize_FunctionHeading(self, node):
        if node.return_type:
            node.return_type = self.optimize(node.return_type)
        
        if hasattr(node, "params") and node.params:
            optimized_params = []
            for param in node.params:
                optimized_params.append(self.optimize(param))
            node.params = optimized_params
        return node
    
    def optimize_Parameter(self, node):
        node.type_name = self.optimize(node.type_name)  # Corrigido: usar type_name
        return node
    
    def optimize_StatementPart(self, node):
        node.statement_sequence = self.optimize(node.statement_sequence)
        return node
    
    def optimize_StatementSequence(self, node):
        optimized_statements = []
        for stmt in node.statements:
            optimized_stmt = self.optimize(stmt)
            if optimized_stmt: 
                optimized_statements.append(optimized_stmt)
        node.statements = optimized_statements
        return node
    
    def optimize_Assignment(self, node):
        node.target = self.optimize(node.target)
        node.value = self.optimize(node.value)
        return node
    
    def optimize_ArrayAssignment(self, node):
        node.array_id = self.optimize(node.array_id)
        node.index = self.optimize(node.index)
        node.value = self.optimize(node.value)
        return node
    
    def optimize_IfStatement(self, node):
        node.condition = self.optimize(node.condition)
        
        if isinstance(node.condition, Literal) and node.condition.type_name == 'BOOL': 
            if node.condition.value == 'true':
                return self.optimize(node.then_branch) 
            elif node.condition.value == 'false':
                if hasattr(node, "else_branch") and node.else_branch: 
                    return self.optimize(node.else_branch)
                else:
                    return None
        
        node.then_branch = self.optimize(node.then_branch) 
        
        if hasattr(node, "else_branch") and node.else_branch: 
            node.else_branch = self.optimize(node.else_branch)
        
        return node
    
    def optimize_WhileStatement(self, node):
        node.condition = self.optimize(node.condition)
        
        if isinstance(node.condition, Literal) and node.condition.type_name == 'BOOL' and node.condition.value == 'false': 
            return None 
        
        node.body = self.optimize(node.body)
        return node
    
    def optimize_RepeatStatement(self, node):
        node.body = self.optimize(node.body)
        node.condition = self.optimize(node.condition)
        
        if isinstance(node.condition, Literal) and node.condition.type_name == 'BOOL' and node.condition.value == 'true': 
            return node.body 
        
        return node
    
    def optimize_ForStatement(self, node):
        node.init = self.optimize(node.init)
        node.limit = self.optimize(node.limit) 
        node.body = self.optimize(node.body)
        return node
    
    def optimize_ProcedureCall(self, node):
        if hasattr(node, "params") and node.params:
            optimized_params = []
            for param in node.params:
                optimized_params.append(self.optimize(param))
            node.params = optimized_params
        return node
    
    def optimize_WritelnStatement(self, node):
        if hasattr(node, "params") and node.params:
            optimized_params = []
            for param in node.params:
                print(f"PARAM\n:{param}\nEND")
                optimized_params.append(self.optimize(param))
            node.params = optimized_params
        return node
    
    def optimize_ReadlnStatement(self, node):
        if hasattr(node, "params") and node.params:
            optimized_params = []
            for param in node.params:
                optimized_params.append(self.optimize(param))
            node.params = optimized_params
        return node
    
    def optimize_BreakStatement(self, node):
        return node
    
    def optimize_ContinueStatement(self, node):
        return node
    
    def optimize_CaseStatement(self, node):
        node.expression = self.optimize(node.expression)
        
        if isinstance(node.expression, Literal):
            value = node.expression.value
            for option in node.case_list:  
                option_value = option.value
                if isinstance(option_value, Literal) and option_value.value == value:
                    return self.optimize(option.statement)
        
        optimized_options = []
        for option in node.case_list: 
            optimized_option = self.optimize_CaseOption(option)
            optimized_options.append(optimized_option)
        node.case_list = optimized_options
        
        return node
    
    def optimize_CaseOption(self, node):
        node.value = self.optimize(node.value)
        node.statement = self.optimize(node.statement)
        return node
    
    def optimize_BinaryOp(self, node):
        node.left = self.optimize(node.left)
        node.right = self.optimize(node.right)
        
        if isinstance(node.left, Literal) and isinstance(node.right, Literal):
            if node.left.type_name == 'NUMBER' and node.right.type_name == 'NUMBER': 
                left_val = self._parse_number(node.left.value)
                right_val = self._parse_number(node.right.value)
                
                if node.operator == '+': 
                    return Literal(left_val + right_val, 'NUMBER')
                elif node.operator == '-': 
                    return Literal(left_val - right_val, 'NUMBER')
                elif node.operator == '*': 
                    return Literal(left_val * right_val, 'NUMBER')
                elif node.operator == '/': 
                    if right_val == 0: 
                        return node
                    return Literal(left_val / right_val, 'NUMBER')
                elif node.operator == 'DIV': 
                    if right_val == 0:
                        return node
                    return Literal(left_val // right_val, 'NUMBER')
                elif node.operator == 'MOD': 
                    if right_val == 0: 
                        return node
                    return Literal(left_val % right_val, 'NUMBER')
                
                elif node.operator == '=':
                    return Literal('true' if left_val == right_val else 'false', 'BOOL')
                elif node.operator == '<>':
                    return Literal('true' if left_val != right_val else 'false', 'BOOL')
                elif node.operator == '<': 
                    return Literal('true' if left_val < right_val else 'false', 'BOOL')
                elif node.operator == '<=': 
                    return Literal('true' if left_val <= right_val else 'false', 'BOOL')
                elif node.operator == '>': 
                    return Literal('true' if left_val > right_val else 'false', 'BOOL')
                elif node.operator == '>=':
                    return Literal('true' if left_val >= right_val else 'false', 'BOOL')
            
            elif node.left.type_name == 'BOOL' and node.right.type_name == 'BOOL': 
                left_val = (node.left.value == 'true')
                right_val = (node.right.value == 'true')
                
                if node.operator == 'AND':
                    return Literal('true' if left_val and right_val else 'false', 'BOOL')
                elif node.operator == 'OR': 
                    return Literal('true' if left_val or right_val else 'false', 'BOOL')
                elif node.operator == '=': 
                    return Literal('true' if left_val == right_val else 'false', 'BOOL')
                elif node.operator == '<>':
                    return Literal('true' if left_val != right_val else 'false', 'BOOL')
            
            elif node.left.type_name == 'PHRASE' and node.right.type_name == 'PHRASE': 
                left_val = self._strip_quotes(node.left.value)
                right_val = self._strip_quotes(node.right.value)
                
                if node.operator == '+': 
                    return Literal(f'"{left_val + right_val}"', 'PHRASE')
                elif node.operator == '=': 
                    return Literal('true' if left_val == right_val else 'false', 'BOOL')
                elif node.operator == '<>':
                    return Literal('true' if left_val != right_val else 'false', 'BOOL')
                elif node.operator == '<':
                    return Literal('true' if left_val < right_val else 'false', 'BOOL')
                elif node.operator == '<=':
                    return Literal('true' if left_val <= right_val else 'false', 'BOOL')
                elif node.operator == '>':
                    return Literal('true' if left_val > right_val else 'false', 'BOOL')
                elif node.operator == '>=':
                    return Literal('true' if left_val >= right_val else 'false', 'BOOL')
        
        if node.operator == '+': 
            if isinstance(node.right, Literal) and node.right.type_name == 'NUMBER' and node.right.value == 0: 
                return node.left
            elif isinstance(node.left, Literal) and node.left.type_name == 'NUMBER' and node.left.value == 0: 
                return node.right
        elif node.operator == '-': 
            if isinstance(node.right, Literal) and node.right.type_name == 'NUMBER' and node.right.value == 0: 
                return node.left
            elif self._nodes_equal(node.left, node.right):
                return Literal(0, 'NUMBER')
        elif node.operator == '*': 
            if isinstance(node.right, Literal) and node.right.type_name == 'NUMBER' and node.right.value == 1: 
                return node.left
            elif isinstance(node.left, Literal) and node.left.type_name == 'NUMBER' and node.left.value == 1: 
                return node.right
            elif (isinstance(node.right, Literal) and node.right.type_name == 'NUMBER' and node.right.value == 0) or \
                 (isinstance(node.left, Literal) and node.left.type_name == 'NUMBER' and node.left.value == 0): 
                return Literal(0, 'NUMBER')
        elif node.operator == '/':
            if isinstance(node.right, Literal) and node.right.type_name == 'NUMBER' and node.right.value == 1: 
                return node.left
            elif isinstance(node.left, Literal) and node.left.type_name == 'NUMBER' and node.left.value == 0 and \
                 not (isinstance(node.right, Literal) and node.right.type_name == 'NUMBER' and node.right.value == 0):
                return Literal(0, 'NUMBER')
        elif node.operator == 'AND':
            if isinstance(node.right, Literal) and node.right.type_name == 'BOOL' and node.right.value == 'false':
                return Literal('false', 'BOOL')
            elif isinstance(node.left, Literal) and node.left.type_name == 'BOOL' and node.left.value == 'false':
                return Literal('false', 'BOOL')
            elif isinstance(node.right, Literal) and node.right.type_name == 'BOOL' and node.right.value == 'true': 
                return node.left
            elif isinstance(node.left, Literal) and node.left.type_name == 'BOOL' and node.left.value == 'true': 
                return node.right
        elif node.operator == 'OR': 
            if isinstance(node.right, Literal) and node.right.type_name == 'BOOL' and node.right.value == 'true': 
                return Literal('true', 'BOOL')
            elif isinstance(node.left, Literal) and node.left.type_name == 'BOOL' and node.left.value == 'true': 
                return Literal('true', 'BOOL')
            elif isinstance(node.right, Literal) and node.right.type_name == 'BOOL' and node.right.value == 'false':
                return node.left
            elif isinstance(node.left, Literal) and node.left.type_name == 'BOOL' and node.left.value == 'false': 
                return node.right
                
        return node
    
    def optimize_UnaryOp(self, node):
        node.operand = self.optimize(node.operand)
        
        if isinstance(node.operand, Literal):
            if node.operator == 'NOT' and node.operand.type_name == 'BOOL': 
                return Literal('false' if node.operand.value == 'true' else 'true', 'BOOL')
            elif node.operator == '-' and node.operand.type_name == 'NUMBER':
                value = self._parse_number(node.operand.value)
                return Literal(-value, 'NUMBER')
        
        if node.operator == 'NOT' and isinstance(node.operand, UnaryOp) and node.operand.operator == 'NOT':
            return node.operand.operand
        
        return node
    
    def optimize_Literal(self, node):
        return node
    
    def optimize_LengthFunction(self, node):
        node.expression = self.optimize(node.expression)
        
        if isinstance(node.expression, Literal) and node.expression.type_name == 'PHRASE': 
            string_value = self._strip_quotes(node.expression.value)
            return Literal(len(string_value), 'NUMBER')
        
        return node
    
    def _parse_number(self, value):
        try:
            if isinstance(value, (int, float)):
                return value
            if '.' in str(value):
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return value
    
    def _strip_quotes(self, value):
        if isinstance(value, str) and len(value) >= 2:
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
        return value
    
    def _nodes_equal(self, node1, node2):
        if not isinstance(node1, type(node2)):
            return False
        
        if isinstance(node1, Literal):
            return node1.value == node2.value and node1.type_name == node2.type_name  
        elif isinstance(node1, Identifier):
            return node1.name == node2.name 
        
        return False
