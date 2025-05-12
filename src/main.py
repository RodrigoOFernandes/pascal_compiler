import sys
from pasAnalex import lexer
from pasSyn import parser, print_ast
from ASTOptimizer import ASTOptimizer
from pasSem import ASTSemanticAnalyzer
from code_generator import Generator

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    print(f"\nCompiling file: {filename}\n")
    
    print("Phase 1: Lexical and syntax analysis...")
    with open(filename, 'r') as file:
        data = file.read()
    
    ast = parser.parse(data)
    if not ast:
        print("Syntax analysis failed.")
        sys.exit(1)
    print("Syntax analysis completed successfully.")
    
    print("\nPhase 2: AST Optimization...")
    optimizer = ASTOptimizer()
    optimized_ast = optimizer.optimize(ast)
    print("AST Optimization completed.")
    
    print("\nOptimized AST:")
    print(print_ast(optimized_ast))
    
    print("\nPhase 3: Semantic Analysis...")
    semantic_analyzer = ASTSemanticAnalyzer()
    if not semantic_analyzer.analyze(optimized_ast):
        print("Semantic analysis failed with errors.")
        sys.exit(1)
    print("Semantic analysis completed successfully.")
    
    
    generator = Generator(filename)
    generator.generate(optimized_ast)


    print("\nCompilation successful!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
