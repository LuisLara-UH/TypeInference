import cmp.nbpackage
import cmp.visitor as visitor

#import G, text
from AST import Node, ProgramNode, DeclarationNode, ExpressionNode
from AST import ClassDeclarationNode, FuncDeclarationNode, AttrDeclarationNode
from AST import VarDeclarationNode, AssignNode, CallNode
from AST import AtomicNode, BinaryNode
from AST import ConstantNumNode, VariableNode, InstantiateNode, PlusNode, MinusNode, StarNode, DivNode
from AST import FormatVisitor, tokenize_text, pprint_tokens

#from cmp.tools.parsing import LR1Parser 
from cmp.evaluation import evaluate_reverse_parse

from cmp.semantic import SemanticError
from cmp.semantic import Attribute, Method, Type
from cmp.semantic import VoidType, ErrorType
from cmp.semantic import Context

def run_pipeline(G, text):
    tokens = tokenize_text(text)
    parser = LR1Parser(G)
    parse, operations = parser([t.token_type for t in tokens], get_shift_reduce=True)
    ast = evaluate_reverse_parse(parse, operations, tokens)
    formatter = FormatVisitor()
    tree = formatter.visit(ast)
    return ast

class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node):
        self.context = Context()
        self.context.create_type('int')
        self.context.create_type('void')
        for declaration in node.declarations:
            self.visit(declaration)
        
    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        try:
            self.context.create_type(node.id)
        except SemanticError as error:
            self.errors.append(error.text)

class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        
    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        self.current_type = self.context.get_type(node.id)
        
        if not node.parent is None:
            try:
                parent = self.context.get_type(node.parent)
                self.current_type.set_parent(parent)
            except SemanticError as error:
                self.errors.append(error.text)
        
        for feature in node.features:
            self.visit(feature)
            
    @visitor.when(AttrDeclarationNode)
    def visit(self, node):
        try:
            att_type = self.context.get_type(node.type)
        except SemanticError as error:
            self.errors.append(error.text)
            att_type = ErrorType()
            
        try:
            self.current_type.define_attribute(node.id, att_type)
        except SemanticError as error:
            self.errors.append(error.text)
            
    @visitor.when(FuncDeclarationNode)
    def visit(self, node):
        try:
            ret_type = self.context.get_type(node.type)
        except SemanticError as error:
            self.errors.append(error.text)
            ret_type = ErrorType()
            
        param_types = []
        for param in node.params:
            try:
                param_types.append(self.context.get_type(param[1]))
            except SemanticError as error:
                self.errors.append(error.text)
                param_types.append(ErrorType())
        
        try:
            self.current_type.define_method(node.id, [param[0] for param in node.params], param_types, ret_type)
        except SemanticError as error:
            self.errors.append(error.text)