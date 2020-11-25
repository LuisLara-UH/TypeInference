from AST import *
import cmp.visitor as visitor
from cmp.semantic import SemanticError
from cmp.semantic import Attribute, Method, Type
from cmp.semantic import VoidType, ErrorType
from cmp.semantic import Context

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