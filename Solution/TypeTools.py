import cmp.nbpackage
import cmp.visitor as visitor

#import G, text
from AST import *
from AST_Visitor import FormatVisitor 
from TokenTools import tokenize_text, pprint_tokens
from TypeChecker import TypeChecker

#from cmp.tools.parsing import LR1Parser 
from cmp.evaluation import evaluate_reverse_parse

from cmp.semantic import SemanticError
from cmp.semantic import Attribute, Method, Type
from cmp.semantic import VoidType, ErrorType
from cmp.semantic import Context

def deprecated_pipeline(G, text):
    tokens = tokenize_text(text)
    parser = LR1Parser(G)
    parse, operations = parser([t.token_type for t in tokens], get_shift_reduce=True)
    ast = evaluate_reverse_parse(parse, operations, tokens)
    formatter = FormatVisitor()
    tree = formatter.visit(ast)
    return ast

def run_pipeline(G, text):
    ast, errors, context = deprecated_pipeline(G, text)
    print('=============== CHECKING TYPES ================')
    checker = TypeChecker(context, errors)
    scope = checker.visit(ast)
    print('Errors: [')
    for error in errors:
        print('\t', error)
    print(']')
    return ast, errors, context, scope