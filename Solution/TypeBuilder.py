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
        self.basic_types = [self.context.get_type('AUTO_TYPE'), self.context.get_type('SELF_TYPE'), self.context.get_type('int'), self.context.get_type('str'), self.context.get_type('bool'), self.context.get_type('void'), self.context.get_type('IO')]
    
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
                if parent in self.basic_types:
                    self.errors.append('Class ' + node.id + ' cant inherit from ' + parent.name)
                    parent = ErrorType()
                self.current_type.set_parent(parent)
                
                actual_type = self.current_type.parent
                while not actual_type is None:
                    if actual_type.parent == self.current_type:
                        self.errors.append('Circular dependency at class ' + node.id)
                        self.current_type.set_parent(ErrorType())
                    actual_type = actual_type.parent

            except SemanticError as error:
                self.errors.append(error.text)
        
        else:
            self.current_type.set_parent(self.context.get_type('object'))

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