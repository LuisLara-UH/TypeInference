from AST import *
import cmp.visitor as visitor
from cmp.semantic import SemanticError
from cmp.semantic import Attribute, Method, Type
from cmp.semantic import VoidType, ErrorType
from cmp.semantic import Context
from cmp.semantic import Scope

WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
METHOD_NOT_DEFINED = 'Method "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'

class TypeChecker:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope=None):
        scope = Scope()
        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())
        return scope

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope):
        self.current_type = self.context.get_type(node.id)
            
        actual_type = self.current_type
        while not actual_type.parent is None:
            actual_type = actual_type.parent
            for attr in actual_type.attributes:
                scope.define_variable(attr.name, attr.type)
                
        new_scope = scope.create_child()
        
        for feature in node.features:
            self.visit(feature, new_scope)
        
    @visitor.when(AttrDeclarationNode)
    def visit(self, node, scope):
        scope.define_variable(node.id, self.context.get_type(node.type))

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        new_scope = scope.create_child()
        
        self.current_method = Method(node.id, [param[0] for param in node.params], [self.context.get_type(param[1]) for param in node.params], self.context.get_type(node.type))

        actual_type = self.current_type
        while not actual_type.parent is None:
            actual_type = actual_type.parent
            for method in actual_type.methods:
                if method.name == self.current_method.name and not self.current_method == method:
                    self.errors.append(WRONG_SIGNATURE % (self.current_method.name, self.current_type.name))
                    
        for param in node.params:
            if new_scope.is_local(param[0]):
                self.errors.append(LOCAL_ALREADY_DEFINED % (param[0], self.current_method.name))
            else:
                new_scope.define_variable(param[0], self.context.get_type(param[1]))
        
        for expr in node.body:
            body_ret_type = self.visit(expr, new_scope)
            
        if not (self.context.get_type(node.type) == self.context.get_type('void') or body_ret_type.conforms_to(self.context.get_type(node.type))):
            self.errors.append(INCOMPATIBLE_TYPES % (body_ret_type.name, self.context.get_type(node.type).name))
        
    @visitor.when(VarDeclarationNode)
    def visit(self, node, scope):
        try:
            var_type = self.context.get_type(node.type)
        except SemanticError as error:
            self.errors.append(error.text)
            var_type = ErrorType()
            
        if scope.is_local(node.id):
            self.errors.append(LOCAL_ALREADY_DEFINED % (node.id, self.current_method.name))
        else:
            scope.define_variable(node.id, var_type)
            
        return var_type
            
    @visitor.when(AssignNode)
    def visit(self, node, scope):
        expr_type = self.visit(node.expr, scope)
        
        if not scope.is_defined(node.id):
            self.errors.append(VARIABLE_NOT_DEFINED % (node.id, self.current_method.name))
        else:
            var_type = scope.find_variable(node.id).type
            if not expr_type.conforms_to(var_type):
                self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, var_type.name))
                
        return expr_type
    
    @visitor.when(CallNode)
    def visit(self, node, scope):
        obj_type = self.visit(node.obj, scope)
        
        if not node.id in [method.name for method in obj_type.methods]:
            self.errors.append(METHOD_NOT_DEFINED % (node.id, obj_type.name))
            return ErrorType()
        
        method = obj_type.get_method(node.id)
        call_args_types = [self.visit(arg, scope) for arg in node.args]
        method_args_types = [param_type for param_type in method.param_types]
        if not len(call_args_types) == len(method_args_types):
            self.errors.append(METHOD_NOT_DEFINED % (node.id, obj_type.name))
        else:
            for i in range(len(call_args_types)):
                if not call_args_types[i].conforms_to(method_args_types[i]):
                    self.errors.append(INCOMPATIBLE_TYPES % (call_args_types[i].name, method_args_types[i].name))
                    
        return method.return_type

    @visitor.when(BinaryNode)
    def visit(self, node, scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        
        if not left_type == right_type and right_type == self.context.get_type('int'):
            self.errors.append(INVALID_OPERATION % (left_type.name, right_type.name))
            
        return self.context.get_type('int')
    
    @visitor.when(ConstantNumNode)
    def visit(self, node, scope):
        return self.context.get_type('int')

    @visitor.when(VariableNode)
    def visit(self, node, scope):
        if not scope.is_defined(node.lex):
            self.errors.append(VARIABLE_NOT_DEFINED % (node.lex, self.current_method.name))
            return ErrorType()
        else:
            return (scope.find_variable(node.lex)).type

    @visitor.when(InstantiateNode)
    def visit(self, node, scope):
        try:
            return self.context.get_type(node.lex)
        except SemanticError as error:
            self.errors.append(error.text)
            return ErrorType()