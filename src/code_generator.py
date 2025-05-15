import os
from ASTNode import *

class Generator:
    def __init__(self, filename):
        self.stack = {}
        base_name = os.path.basename(filename)
        file_name_without_ext = os.path.splitext(base_name)[0] 
        self.filename = f"../vm/{file_name_without_ext}.vm"
        with open(self.filename, 'w') as f:
            f.write('')
        self.op_stack_pos = 0
        self.loop_counter = 0
        self.if_counter = 0
        self.types = {}

    def generate(self, ast):
       self.visit(ast) 
       print("Code generation completed")
    
    def visit(self, node):
        if node is None:
            return None 

        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        print(f"Warning: No visitor defined for {node.__class__.__name__}")
        return None

    def visit_Program(self, node):
        self.visit(node.header)
        self.visit(node.block)
        return None 

    def visit_Header(self, node):
        return None 

    def visit_Block(self, node):
        if node.var_decl_part:
            self.visit(node.var_decl_part)

        if node.statement_part:
            self.visit(node.statement_part)

        return None 

    def visit_VarDeclarationPart(self, node):
        if hasattr(node, "declarations") and node.declarations:
            for decl in node.declarations:
                self.visit(decl)
        return None

    def visit_VarDeclaration(self, node):
       for id in node.id_list:
           var_name = self.visit(id)
           self.types[var_name] = self.visit(node.type_name).lower() 
       return None

    def visit_IdList(self, node):
        var_list = []
        for id in node.ids:
            var_name = self.visit(id)
            var_list.append(var_name)

        return var_list

    def visit_StatementPart(self, node):
        self.visit(node.statement_sequence)
        return None

    def visit_StatementSequence(self, node):
        for statement in node.statements:
            self.visit(statement)
        return None

    def visit_Assignment(self, node):
        target_name = self.visit(node.target)

        if isinstance(node.value, Literal):
            value_type, value = self.visit(node.value)
            if value_type == "NUMBER":
                value = int(value)
                command = f"pushi {value}\n"
                with open(self.filename, 'a') as f:
                    f.write(command)
                self.stack[target_name] = self.op_stack_pos
                self.op_stack_pos += 1
                command = f"storeg {self.stack[target_name]}\n"
                with open(self.filename, 'a') as f:
                    f.write(command)
        
        elif isinstance(node.value, LengthFunction):
            expr = self.visit(node.value.expression)
            if isinstance(node.value.expression, Identifier):
                command = f"pushg {self.stack[expr]}\n"
                with open(self.filename, 'a') as f:
                    f.write(command)
            
            command = "strlen\n"
            with open(self.filename, 'a') as f:
                f.write(command)

            if target_name not in self.stack:
                self.stack[target_name] = self.op_stack_pos
                self.op_stack_pos += 1
                
            command = f"storeg {self.stack[target_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command) 

        elif isinstance(node.value, BinaryOp):
            self.visit(node.value)
            
            if target_name not in self.stack:
                self.stack[target_name] = self.op_stack_pos
                self.op_stack_pos += 1
            
            command = f"storeg {self.stack[target_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command)

        elif isinstance(node.value, Identifier):
            var_name = self.visit(node.value)
            
            if target_name not in self.stack:
                self.stack[target_name] = self.op_stack_pos
                self.op_stack_pos += 1

            command = f"pushg {self.stack[var_name]}\nstoreg {self.stack[target_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command)

        return target_name
    
    def visit_WritelnStatement(self, node):
        if node.params is not None:
            for param in node.params:
                if isinstance(param, Literal):
                    param_type, phrase = self.visit(param) 
                    phrase = phrase[1:-1]
                    phrase = phrase.replace('"', '\\"')
                    command = f'pushs "{phrase}"\nwrites\n'
                    with open(self.filename, 'a') as f:
                        f.write(command)
                if isinstance(param, Identifier):
                   param_name = self.visit(param)
                   if self.types[param_name] == "integer":
                       command = f"pushg {self.stack[param_name]}\nwritei\n" 
                       with open(self.filename, 'a') as f:
                           f.write(command)

        command = "writeln\n" 
        with open(self.filename, 'a') as f:
            f.write(command)
        return None

    def visit_ReadlnStatement(self, node):
        if node.params is not None:
            for param in node.params:
                if isinstance(param, ArrayId):
                    array_name = self.visit(param)
                    if self.types[array_name] == "integer":
                        command = f"read\natoi\n"
                        with open(self.filename, 'a') as f:
                            f.write(command)
                        self.stack[array_name] = self.op_stack_pos
                        self.op_stack_pos += 1

                if isinstance(param, Identifier):
                    var_name = self.visit(param)
                    if self.types[var_name] == "string":
                        command = f"read\n"
                        with open(self.filename, 'a') as f:
                            f.write(command)
                        self.stack[var_name] = self.op_stack_pos
                        self.op_stack_pos += 1
                    elif self.types[var_name] == "integer":
                        command = f"read\natoi\n"
                        with open(self.filename, 'a') as f:
                            f.write(command)
                        self.stack[var_name] = self.op_stack_pos
                        self.op_stack_pos += 1



    def visit_ForStatement(self, node):
        init_var_name = self.visit(node.init)
        
        loop_start_label = f"FOR{self.loop_counter}"
        loop_end_label = f"OUT{self.loop_counter}"
        self.loop_counter += 1
      
        limit = None
        if isinstance(node.limit, Literal):
            limit_type, limit = self.visit(node.limit)
        elif isinstance(node.limit, Identifier):
            limit_name = self.visit(node.limit)

        if node.direction == "to":
            with open(self.filename, 'a') as f:
                f.write(f"{loop_start_label}:\n")
           
            if limit is not None:
                command = f"pushg {self.stack[init_var_name]}\npushi {limit}\ninfeq\njz {loop_end_label}\n"
            else:
                command = f"pushg {self.stack[init_var_name]}\npushg {self.stack[limit_name]}\ninfeq\njz {loop_end_label}\n"

            with open(self.filename, 'a') as f:
                f.write(command)
            
            self.visit(node.body)

            command = f"pushg {self.stack[init_var_name]}\npushi 1\nadd\nstoreg {self.stack[init_var_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command)
            
            command = f"jump {loop_start_label}\n"
            with open(self.filename, 'a') as f:
                f.write(command)

            with open(self.filename, 'a') as f:
                f.write(f"{loop_end_label}:\n")
        else:
            with open(self.filename, 'a') as f:
                f.write(f"{loop_start_label}:\n")
           
            command = f"pushg {self.stack[init_var_name]}\npushi {limit}\nsupeq\njz {loop_end_label}\n"
            with open(self.filename, 'a') as f:
                f.write(command)

            self.visit(node.body)
            
            command = f"pushg {self.stack[init_var_name]}\npushi 1\nsub\nstoreg {self.stack[init_var_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command)

            command = f"jump {loop_start_label}\n"
            with open(self.filename, 'a') as f:
                f.write(command)

            with open(self.filename, 'a') as f:
                f.write(f"{loop_end_label}:\n")

    def visit_WhileStatement(self, node):
        loop_start_label = f"WHILE{self.loop_counter}"
        loop_end_label = f"ENDWHILE{self.loop_counter}"
        self.loop_counter += 1
        
        with open(self.filename, 'a') as f:
            f.write(f"{loop_start_label}:\n")
        
        self.visit(node.condition)
        
        command = f"jz {loop_end_label}\n"
        with open(self.filename, 'a') as f:
            f.write(command)
        
        self.visit(node.body)
        
        command = f"jump {loop_start_label}\n"
        with open(self.filename, 'a') as f:
            f.write(command)
        
        with open(self.filename, 'a') as f:
            f.write(f"{loop_end_label}:\n")
        
        return None

    def visit_IfStatement(self, node):
        self.visit(node.condition)

        else_label = f"ELSE{self.if_counter}"
        end_if_label = f"ENDIF{self.if_counter}"
        self.if_counter += 1

        command = f"jz {else_label}\n"
        with open(self.filename, 'a') as f:
            f.write(command)

        self.visit(node.then_branch)

        command = f"jump {end_if_label}\n"
        with open(self.filename, 'a') as f:
            f.write(command)

        with open(self.filename, 'a') as f:
            f.write(f"{else_label}:\n")
        
        if node.else_branch:
            self.visit(node.else_branch)

        with open(self.filename, 'a') as f:
            f.write(f"{end_if_label}:\n")
            
        return None

    def visit_BinaryOp(self, node):
        if isinstance(node.left, Identifier):
            left_name = self.visit(node.left)
            command = f"pushg {self.stack[left_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command)
        elif isinstance(node.left, Literal):
            left_type, left_value = self.visit(node.left)
            command = f"pushi {left_value}\n"
            with open(self.filename, 'a') as f:
                f.write(command)
        elif isinstance(node.left, ArrayId):
            array_name = self.visit(node.left)
            command = f"pushg {self.stack[array_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command)

            if self.types[array_name] == "string":
               pascal_index = self.visit(node.left.expression) 
               command = f"pushg {self.stack[pascal_index]}\npushi 1\nsub\ncharat\n"
               with open(self.filename, 'a') as f:
                   f.write(command)
        elif isinstance(node.left, BinaryOp):
            self.visit(node.left)

        if isinstance(node.right, ArrayId):
            array_name = self.visit(node.right)
            command = f"pushg {self.stack[array_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command)
        elif isinstance(node.right, Identifier):
            right_name = self.visit(node.right)
            command = f"pushg {self.stack[right_name]}\n"
            with open(self.filename, 'a') as f:
                f.write(command)
        elif isinstance(node.right, Literal):
            right_type, right_value = self.visit(node.right)
            if right_type == "NUMBER":
                command = f"pushi {right_value}\n"
                with open(self.filename, 'a') as f:
                    f.write(command)
            elif right_type == "PHRASE":
                right_value = right_value[1:-1]
                right_value = f'"{right_value}"'
                command = f"pushs {right_value}\npushi 0\ncharat\n"
                with open(self.filename, 'a') as f:
                    f.write(command)
        elif isinstance(node.right, BinaryOp):
            self.visit(node.right)

        if node.operator == '+':
            command = f"add\n"
            with open(self.filename, 'a') as f:
                f.write(command)
        elif node.operator == '-':
            command = f"sub\n"
            with open(self.filename, 'a') as f:
                f.write(command)
        elif node.operator == '*':
            command = f"mul\n"
            with open(self.filename, 'a') as f:
                f.write(command)
        elif node.operator == 'div':
            command = f"div\n"
            with open(self.filename, 'a') as f:
                f.write(command)

        elif node.operator == 'mod':
            command = f"mod\n"
            with open(self.filename, 'a') as f:
                f.write(command)
                
        elif node.operator == '=':
            command = f"equal\n"
            with open(self.filename, 'a') as f:
                f.write(command)
        
        elif node.operator == '>':
            command = f"sup\n"
            with open(self.filename, 'a') as f:
                f.write(command)

        elif node.operator == '<':
            command = f"inf\n"
            with open(self.filename, 'a') as f:
                f.write(command)

        elif node.operator == '<=':
            command = f"infeq\n"
            with open(self.filename, 'a') as f:
                f.write(command)

        elif node.operator == '>=':
            command = f"supeq\n"
            with open(self.filename, 'a') as f:
                f.write(command)
            
        elif node.operator == 'and':
            command = f"and\n"
            with open(self.filename, 'a') as f:
                f.write(command)
            
        elif node.operator == 'or':
            command = f"or\n"
            with open(self.filename, 'a') as f:
                f.write(command)



    def visit_Identifier(self, node):
        return node.name

    def visit_Literal(self, node):
        return node.type_name, node.value

    def visit_ArrayId(self, node):
        return node.id_name

    def visit_ArrayType(self, node):
        return self.visit(node.element_type) 

    def visit_Type(self, node):
        return node.type_name
