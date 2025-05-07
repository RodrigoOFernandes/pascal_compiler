from ASTNode import *

class NodeVisitor:
    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        print(f"Warning: No visit method found for {node.__class__.__name__}")


class ASTNodeVisitor(NodeVisitor):
    def visit_Program(self, node):
        return self.visit(node.header) + self.visit(node.block)
    
    def visit_Header(self, node):
        return {"program_name": node.id}
    
    def visit_Block(self, node):
        result = {}
        
        result["var_declarations"] = self.visit(node.var_declaration_part)
        
        if hasattr(node, "proc_or_func") and node.proc_or_func:
            result["procedures_functions"] = [self.visit(pf) for pf in node.proc_or_func]
        
        if hasattr(node, "additional_var_declaration_part") and node.additional_var_declaration_part:
            result["additional_vars"] = self.visit(node.additional_var_declaration_part)
        
        result["statements"] = self.visit(node.statement_part)
        
        return result
    
    
    def visit_VarDeclarationPart(self, node):
        if hasattr(node, "declarations") and node.declarations:
            return [self.visit(decl) for decl in node.declarations]
        return []
    
    def visit_VarDeclaration(self, node):
        id_list = [self.visit(id_node) for id_node in node.id_list]
        type_info = self.visit(node.type)
        return {"identifiers": id_list, "type": type_info}
    
    
    def visit_Type(self, node):
        return {"type_name": node.type_name}
    
    def visit_ArrayType(self, node):
        range_info = self.visit(node.range) if hasattr(node, "range") else None
        element_type = self.visit(node.element_type)
        return {"type": "array", "range": range_info, "element_type": element_type}
    
    
    def visit_Identifier(self, node):
        return {"name": node.id, "kind": "identifier"}
    
    def visit_ArrayId(self, node):
        index_expr = self.visit(node.expression)
        return {"name": node.id, "kind": "array_access", "index": index_expr}
    
    
    def visit_ProcedureDeclaration(self, node):
        heading = self.visit(node.heading)
        block = self.visit(node.block)
        return {"kind": "procedure", "heading": heading, "block": block}
    
    def visit_FunctionDeclaration(self, node):
        heading = self.visit(node.heading)
        block = self.visit(node.block)
        return {"kind": "function", "heading": heading, "block": block}
    
    def visit_ProcedureHeading(self, node):
        result = {"name": node.id}
        
        if hasattr(node, "parameters") and node.parameters:
            result["parameters"] = [self.visit(param) for param in node.parameters]
        
        return result
    
    def visit_FunctionHeading(self, node):
        result = {}
        
        if node.id:
            result["name"] = node.id
        
        result["return_type"] = self.visit(node.return_type)
        
        if hasattr(node, "parameters") and node.parameters:
            result["parameters"] = [self.visit(param) for param in node.parameters]
        
        return result
    
    def visit_Parameter(self, node):
        return {"name": node.id, "type": self.visit(node.type)}
    
    
    def visit_StatementPart(self, node):
        return self.visit(node.statement_sequence)
    
    def visit_StatementSequence(self, node):
        return [self.visit(stmt) for stmt in node.statements]
    
    def visit_Assignment(self, node):
        target = self.visit(node.target)
        value = self.visit(node.value)
        return {"kind": "assignment", "target": target, "value": value}
    
    def visit_ArrayAssignment(self, node):
        index = self.visit(node.index)
        value = self.visit(node.value)
        return {"kind": "array_assignment", "array": node.id, "index": index, "value": value}
    
    def visit_IfStatement(self, node):
        result = {
            "kind": "if",
            "condition": self.visit(node.condition),
            "then_branch": self.visit(node.then_stmt)
        }
        
        if hasattr(node, "else_stmt") and node.else_stmt:
            result["else_branch"] = self.visit(node.else_stmt)
        
        return result
    
    def visit_WhileStatement(self, node):
        condition = self.visit(node.condition)
        body = self.visit(node.body)
        return {"kind": "while", "condition": condition, "body": body}
    
    def visit_RepeatStatement(self, node):
        body = self.visit(node.body)
        condition = self.visit(node.condition)
        return {"kind": "repeat", "body": body, "condition": condition}
    
    def visit_ForStatement(self, node):
        init = self.visit(node.init)
        direction = node.direction if hasattr(node, "direction") else "to"
        target = self.visit(node.target)
        body = self.visit(node.body)
        
        return {"kind": "for", "init": init, "direction": direction, "target": target, "body": body}
    
    def visit_ProcedureCall(self, node):
        result = {"kind": "procedure_call", "name": node.id}
        
        if hasattr(node, "params") and node.params:
            result["parameters"] = [self.visit(param) for param in node.params]
        
        return result
    
    def visit_WritelnStatement(self, node):
        result = {"kind": "writeln"}
        
        if hasattr(node, "params") and node.params:
            result["parameters"] = [self.visit(param) for param in node.params]
        
        return result
    
    def visit_ReadlnStatement(self, node):
        result = {"kind": "readln"}
        
        if hasattr(node, "ids") and node.ids:
            result["variables"] = [self.visit(id_node) for id_node in node.ids]
        
        return result
    
    def visit_BreakStatement(self, node):
        return {"kind": "break"}
    
    def visit_ContinueStatement(self, node):
        return {"kind": "continue"}
    
    def visit_CaseStatement(self, node):
        expr = self.visit(node.expression)
        options = [self.visit(opt) for opt in node.options]
        
        return {"kind": "case", "expression": expr, "options": options}
    
    def visit_CaseOption(self, node):
        value = self.visit(node.value)
        statement = self.visit(node.statement)
        
        return {"value": value, "statement": statement}
    
    
    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        return {"kind": "binary_op", "operator": node.op, "left": left, "right": right}
    
    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        
        return {"kind": "unary_op", "operator": node.op, "operand": operand}
    
    def visit_Literal(self, node):
        return {"kind": "literal", "value": node.value, "type": node.type}
    
    def visit_LengthFunction(self, node):
        expr = self.visit(node.expression)
        
        return {"kind": "length_function", "expression": expr}
