import sys
from ASTOptimizer import ASTOptimizer
from pasAnalex import *
from ASTNode import *
from pasSyn import parser, print_ast



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
            return False 
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
        if isinstance(ast, Program):
            self.visit_program(ast)
        
        return len(self.errors) == 0, self.errors
    
    def error(self, message, node=None):
        node_info = f" at {node.__class__.__name__}" if node else ""
        self.errors.append(f"Semantic Error{node_info}: {message}")
    
    def enter_scope(self):
        self.current_scope = SymbolTable(self.current_scope)
    
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def visit_program(self, node):
        self.visit_block(node.block)
    



def optimize_ast(ast):
    optimizer = ASTOptimizer()
    optimized_ast = optimizer.optimize(ast)
    return optimized_ast

def main():
    if len(sys.argv) != 2:
        print("Usage: python optimize_ast.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    with open(filename, 'r') as file:
        data = file.read()
    
    print(f"\nParsing file: {filename}\n")
    
    ast = parser.parse(data)
    
    print("\nParsing completed successfully!")
    
    print("\nOriginal AST:")
    original_ast_str = print_ast(ast)
    print(original_ast_str)
    
    print("\nOptimizing AST...")
    optimized_ast = optimize_ast(ast)
    
    print("\nOptimized AST:")
    optimized_ast_str = print_ast(optimized_ast)
    print(optimized_ast_str)
    
    semantic_analyzer = SemanticAnalyzer()
    success, errors = semantic_analyzer.analyze(optimized_ast)

    if success:
        print("Analise semantica concluida com sucesso")
    else:
        for error in errors:
            print(f"Foram encontrados os seguintes erros semanticos: {error}\n")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()

