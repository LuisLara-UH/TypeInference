import cmp.nbpackage
import cmp.visitor as visitor

#import G, text
from AST import *
from AST_Visitor import FormatVisitor 
from TokenTools import tokenize_text, pprint_tokens
from TypeChecker import TypeChecker
from TypeCollector import *
from TypeBuilder import *

from cmp.semantic import SemanticError
from cmp.semantic import Attribute, Method, Type
from cmp.semantic import VoidType, ErrorType
from cmp.semantic import Context

from LR1 import LR1Parser
from cmp.evaluation import evaluate_reverse_parse
from Grammar import get_grammar

G, _, _, _, _, _, _ = get_grammar()

def run_pipeline(text):
    ret_text = '\n' + '=================== TEXT ======================'
    ret_text += '\n' + text
    ret_text += '\n' + '================== TOKENS ====================='
    tokens = tokenize_text(text)
    ret_text += '\n' + pprint_tokens(tokens)
    ret_text += '\n' + '=================== PARSE ====================='
    ret_text += '\n'
    parser = LR1Parser(G)
    ret_parser = parser([t.token_type for t in tokens])
    parse, operations = ret_parser
    if parse is None:
        return ret_text + "\nParsing Error at " + operations
    ret_text += '\n'.join(repr(x) for x in parse)
    ret_text += '\n' + '==================== AST ======================'
    ast = evaluate_reverse_parse(parse, operations, tokens)
    formatter = FormatVisitor()
    tree = formatter.visit(ast)
    ret_text += '\n' + tree

    ret_text += '\n' + '============== COLLECTING TYPES ==============='
    errors = []
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context
    ret_text += '\n' + 'Errors:'
    for error in errors:
        ret_text += '\n' + error
    ret_text += '\n' + 'Context:'
    ret_text += '\n' + str(context)
    ret_text += '\n' + '=============== BUILDING TYPES ================'
    builder = TypeBuilder(context, errors)
    builder.visit(ast)
    ret_text += '\n' + 'Errors: ['
    for error in errors:
        ret_text += '\n' + '\t'
        ret_text += '\n' + error
    ret_text += '\n' + ']'
    ret_text += '\n' + 'Context:'
    ret_text += '\n' + str(context)

    ret_text += '\n' + '=============== CHECKING TYPES ================'
    checker = TypeChecker(context, errors)
    try:
        scope, errors = checker.visit(ast)
        while(checker.changed):
            scope, errors = checker.visit(ast)
    except SemanticError as e:
        errors = [e.text]
    ret_text += '\n' + 'Errors: ['
    for error in errors:
        ret_text += '\n' + '\t'
        ret_text += '\n' + error
    ret_text += '\n' + ']'
    if len(errors) == 0:
        checker.printer(ast)

    return ret_text