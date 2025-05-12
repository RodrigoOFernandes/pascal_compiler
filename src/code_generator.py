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
       var_names = self.visit(node.id_list) 
       var_type = node.type_name
       if var_names is not None:
           for var in var_names:
               print("VAR DEBUG")
               print(var_type)
               self.types[var] = var_type

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
        if isinstance(node.target, Identifier):
            target_name = self.visit(node.target)
            value_type, value = self.visit(node.value)
            self.stack[target_name] = self.op_stack_pos
            self.op_stack_pos += 1
            if value_type == "NUMBER":
                command = f"pushi {value}\n"
                with open(self.filename, 'a') as f:
                    f.write(command)
        return None
    
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
        return None

    def visit_ReadlnStatement(self, node):
        if node.params is not None:
            for param in node.params:
                if isinstance(param, ArrayId):
                    array_name = self.visit(param)
                    print("DEBUG\n")
                    print(array_name)
                    print(self.types[array_name])
                    if self.types[array_name] == "integer":
                        command = f"read\natoi\n"
                        self.op_stack_pos += 1
                        with open(self.filename, 'w') as f:
                            f.write(command)

    def visit_ForStatement(self, node):
        label = f"FOR{self.loop_counter}"
        self.loop_counter += 1 
        
        if node.direction == "TO":
            self.visit(node.init)
            limit_type, limit = self.visit(node.limit)
            if limit_type == "NUMBER":
                command = f"pushi {limit}\n"
                self.op_stack_pos += 1
                with open(self.filename, 'a') as f:
                    f.write(command)

        self.visit(node.body) 

    def visit_Identifier(self, node):
        return node.name

    def visit_Literal(self, node):
        return node.type_name, node.value

    def visit_ArrayId(self, node):
        return node.id_name

