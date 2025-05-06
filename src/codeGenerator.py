import sys
from pasAnalex import *  
from pasSemantic import *
from ply import yacc

class CodeGenerator:
    def __init__(self, symbol_table):
        self.output = []
        self.label_counter = 0
        self.symbol_table = symbol_table
        self.current_scope = [] 
        self.loop_stack = [] 
        self.current_function = None  
        
        self.global_offset = 0
        self.local_offset = 0
        
        self.var_addresses = {} 

    def new_label(self):
        """Gera um novo rótulo único"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def emit(self, instruction):
        """Adiciona instrução ao código de saída"""
        self.output.append(instruction)

    def get_code(self):
        """Retorna o código completo"""
        return "\n".join(self.output)

    # --- Principais funções de geração de código ---
    
    def generate_program(self, name, block):
        """Gera código para o programa principal"""
        self.emit(f"; Código para o programa {name}")
        self.emit("START")
        
        self.current_scope.append("global")
        
        self.generate_block(block)
        
        # Encerra o programa
        self.emit("STOP")
        return self.get_code()
