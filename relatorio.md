#Compilador de Pascal Standard em Python

##Introudução
Este projeto foi realizado com o objetivo de fazer um compilador para Pascal Standard usando a ferramnenta yacc do python. Começamos pelo analizador lexico, tendo sempre em conta os 7 testes de código Pascal que nos foram fornecidos, depois partimos para a escrita da gramática com construção da AST. que depois é otimizada. Por fim, realizamos análise sintática e a geração do código da maquina virtual.

##Analizador Léxico
###Definição dos Tokens
###Expressões Regulares para Tokens Simples
###Palavras Reservadas (Case-Insensitive)
###Identificadores e Literais
###Tratamento de Comentários e Espaços
###Tratamento de Erros
###Teste do Lexer test_lexer(data): 

##Analizador Sintático
###(FALAR DA GRAMATICA)
###A AST (Abstract Syntax Tree) é uma representação hierárquica simplificada da estrutura sintática do código fonte, eliminando detalhes irrelevantes (como símbolos de pontuação) e mantendo apenas a lógica essencial do programa.

No analisador sintático fornecido, a AST é construída a cada regra de produção usando classes específicas (como Program, IfStatement, BinaryOp, etc.), que herdam de uma classe base ASTNode.

1. Estrutura da AST
Cada nó da AST é um objeto que representa:

Declarações (programas, variáveis, funções).

Comandos (atribuições, loops, condicionais).

Expressões (operações matemáticas, lógicas, chamadas de funções).

Exemplo de nós comuns:

Classe (Nó)	Exemplo no Pascal	Representação na AST
Program	program MeuProg; begin ... end.	Program(Header("MeuProg"), Block(...))
IfStatement	if x > 0 then ... else ...	IfStatement(BinaryOp(>, x, 0), ..., ...)
BinaryOp	a + b * c	BinaryOp(+, a, BinaryOp(*, b, c))
Assignment	x := 10	Assignment(Identifier("x"), Literal(10))
2. Construção Passo a Passo
(a) Regras de Produção → Nós da AST
Cada função p_* no analisador sintático:

Recebe os tokens (t[1], t[2], etc.) da regra correspondente.

Combina esses tokens em um objeto AST e armazena em t[0].

Exemplo 1: Atribuição (:=)

python
def p_assignment_statement(t):
    """assignment_statement : ID ASSIGN expression"""
    t[0] = Assignment(Identifier(t[1]), t[3])  # Ex: x := 10 → Assignment("x", Literal(10))
Exemplo 2: Operação Binária (+, -, *, etc.)

python
def p_expression_m(t):
    """expression_m : expression_m sign expression_s"""
    t[0] = BinaryOp(t[1], t[2], t[3])  # Ex: a + b → BinaryOp(a, +, b)
(b) Hierarquia da AST
A AST é construída recursivamente, onde nós complexos contêm subárvores.

Exemplo:

pascal
if x > 0 then 
    y := x * 2 
else 
    y := 0
AST gerada:

IfStatement(
    condition=BinaryOp(>, Identifier("x"), Literal(0)),
    then_part=Assignment(Identifier("y"), BinaryOp(*, Identifier("x"), Literal(2))),
    else_part=Assignment(Identifier("y"), Literal(0))
)

##Otimizador de AST
O otimizador percorre a Árvore Sintática Abstrata (AST) e aplica transformações para simplificar o código, removendo redundâncias e pré-calculando expressões sempre que possível.

1. Estrutura do Otimizador
Método principal: optimize(node)

Chama métodos específicos para cada tipo de nó (ex: optimize_IfStatement, optimize_BinaryOp).

Se não houver um método específico, usa generic_optimize (que apenas retorna o nó sem modificações).

2. Tipos de Otimizações Realizadas
(a) Simplificação de Expressões Constantes
Operações aritméticas/lógicas com literais:

Ex: 5 + 3 → 8

Ex: true AND false → false

Ex: "hello" + " " + "world" → "hello world"

Condicionais com condições constantes:

Ex: if true then X else Y → X

Ex: if false then X else Y → Y

Ex: while false do ... → (remove o loop inteiro)

Exemplo em código:

Operações com valores neutros:

Ex: x + 0 → x

Ex: x * 1 → x

Ex: x AND true → x

Exemplo em código:

Funções com parâmetros constantes:

Ex: Length("abc") → 3

Exemplo em código:

Dupla negação:

Ex: NOT (NOT x) → x

Exemplo em código:

4. Métodos Auxiliares
_parse_number: Converte strings numéricas para int ou float.

_strip_quotes: Remove aspas de strings literais (ex: "abc" → abc).

_nodes_equal: Compara dois nós para verificar equivalência (usado em simplificações como x - x = 0).

5. Saída
A AST é modificada in-place, com nós substituídos por versões otimizadas.

Nós removidos (como loops mortos) são retornados como None e eliminados na etapa de reconstrução. 


##Analizador Semântico 
Este analisador semântico verifica a correção estática do código Pascal após a fase sintática, garantindo que:

Todas as variáveis e funções estão declaradas antes do uso.

Tipos de dados são compatíveis em operações, atribuições e parâmetros.

Regras de escopo são respeitadas (ex: variáveis locais vs. globais).

Estruturas de controle (if, while, for) têm condições booleanas válidas.

Chamadas de funções/procedimentos têm a quantidade e tipos de parâmetros corretos.

1. Componentes Principais
(a) Tabela de Símbolos (SymbolTable)
Armazena informações sobre variáveis, funções, procedimentos e arrays em escopos aninhados.

Estrutura:

symbols: Dicionário que mapeia nomes a objetos Symbol.

parent: Referência ao escopo pai (para suporte a escopos aninhados).

(b) Símbolos (Symbol, ProcedureSymbol, ArraySymbol)
Symbol: Representa variáveis simples (nome, tipo, se é constante, se foi inicializada).

ProcedureSymbol: Armazena informações de funções/procedimentos (parâmetros, tipo de retorno).

ArraySymbol: Guarda o tipo dos elementos e dimensões (ex: ARRAY [1..10] OF INTEGER).

(c) Regras de Compatibilidade de Tipos
type_compatibility: Define quais tipos podem ser convertidos implicitamente (ex: INTEGER → REAL).

operator_rules: Especifica os tipos válidos para cada operador (ex: + só funciona com INTEGER, REAL, ou STRING).

##Gerador de Código
Este módulo (Generator) é responsável por traduzir a AST (Árvore Sintática Abstrata) em código de máquina virtual, gerando um arquivo .vm que pode ser executado por uma máquina virtual simples.

1. Funcionamento Geral
Entrada: AST gerada pelo analisador semântico.

Saída: Arquivo .vm com instruções em uma linguagem de baixo nível (stack-based).

Objetivo: Converter estruturas Pascal (variáveis, loops, funções) em operações de pilha e saltos condicionais.

2. Componentes Principais
(a) Tabelas de Símbolos
stack: Mapeia variáveis globais para posições na memória.

function_stack: Mapeia variáveis locais (de funções) para posições na pilha.

types: Armazena os tipos das variáveis (ex: integer, string).

(b) Contadores
op_stack_pos: Controla a posição atual na pilha de operações.

loop_counter, if_counter: Geram rótulos únicos para loops e condicionais.

(c) Flags de Estado
in_function: Indica se o gerador está processando uma função.

has_function: Indica se o programa tem funções/procedimentos.




##Conclusão
Embora tenhamos concluído o projeto com muitas funcionalidades, notamos que como o Pascal é uma linguagem com muitas particularidades podiamos sempre melhorar ou adicionar mais alguma coisa, como lidar com apontadores, maior variedade possibilidades na geração de código, etc. No entanto, consideramos este projeto uma grande oportunidade de aprendizagem não só sobre Pascal, mas também lingugaens de programçãp em geral.
