import ply.yacc as yacc 
from pasAnalex import tokens

'''
GRAMMAR:

program: PROGRAM ID SEMICOLON routine DOT
        |PROGRAM ID SEMICOLON routine
        |PROGRAM ID routine DOT
        |PROGRAM ID routine

routine: routine_head routine_body

routine_head: const_part type_part var_part routine_part 

var_part: $
         | VAR var_decl_list 

var_decl_list: var_decl_list var_decl 
              |var_decl 

var_decl: name_list COLON type_decl SEMICOLON
         |name_list COLON type_decl

name_list: name_list COMMA ID
           | ID 

'''
