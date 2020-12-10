from AST import *
import cmp.visitor as visitor
from cmp.semantic import SemanticError
from cmp.semantic import Attribute, Method, Type
from cmp.semantic import VoidType, ErrorType
from cmp.semantic import Context

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

        parent_type = self.context.create_type('Object')
        child_types = [self.context.create_type('String'), self.context.create_type('Int'), self.context.create_type('Bool'), self.context.create_type('IO'), self.context.create_type('void'), self.context.create_type('SELF_TYPE'), self.context.create_type('AUTO_TYPE')]
        for child in child_types:
            child.set_parent(parent_type)

        for declaration in node.declarations:
            self.visit(declaration)
        
    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        try:
            self.context.create_type(node.id)
        except SemanticError as error:
            self.errors.append(error.text)