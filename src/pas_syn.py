import ply.yacc as yacc 
from pasAnalex import tokens

'''
GRAMMAR:

program: PROGRAM ID SEMICOLON block

block: var_expression | code

var_expression: ID COLON ID SEMICOLON | 

code: BEGIN ID END.

'''
