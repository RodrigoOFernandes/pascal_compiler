import sys
from ASTOptimizer import ASTOptimizer
from pasAnalex import *
from ASTNode import *
from pasSyn import parser, print_ast

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
    
    return optimized_ast

if __name__ == "__main__":
    main()

