from AST import *
import cmp.visitor as visitor
from cmp.semantic import SemanticError
from cmp.semantic import Attribute, Method, Type
from cmp.semantic import VoidType, ErrorType
from cmp.semantic import Context
from cmp.semantic import Scope

def common_ancestor(type_list):
    
    visited = []
    
    actual_type = type_list[0]
    print(type_list)

    for t in type_list:
        if t.name == '<error>':
            return ErrorType()
        if not t.name == 'AUTO_TYPE':
            actual_type = t

    visited.append(actual_type)

    while not actual_type.parent is None:
        actual_type = actual_type.parent
        visited.append(actual_type)

    print('visited', visited)
    for t in visited:
        ok = True
        for types in type_list:
            if not types.conforms_to(t):
                ok = False
                break
        if ok:
            print(t.name)
            return t

    print("sali del ciclo y soy mongo")         
        


WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
ATTRIBUTE_OVERWRITTEN = 'Attribute "%s" cant be overwritten.'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
METHOD_NOT_DEFINED = 'Method "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'
AUTO_TYPE_ERROR = 'Couldnt infer type of "%s"'
TYPE_NOT_DEFINED = 'Type "%s" is not defined'

class TypeChecker:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors
        self.changed_atts = {}
        self.changed_methods = {}
        self.at = self.context.get_type('AUTO_TYPE')

    @visitor.on('node')
    def visit(self, node, scope, type_suggested):
        pass
    
    @visitor.on('node')
    def printer(self, node):
        pass

    @visitor.when(ProgramNode)
    def printer(self, node):
        
        for dec in node.declarations:
            if dec.parent is None:
                print("class " + dec.id + " { ")
            else:
                print("class " + dec.id + " inherits " + dec.parent + " { ")

            self.printer(dec)
            print("};")  

    @visitor.when(ClassDeclarationNode)
    def printer(self, node):
        for feat in node.features:
            self.current_type = self.context.get_type(node.id)
            self.printer(feat)

    @visitor.when(AttrDeclarationNode)
    def printer(self, node):
        if node.type == self.at.name:
            print(node.id + " : " + self.changed_atts[(node.id, self.current_type)].name)
        else:
            print(node.id + " : " + node.type)

    @visitor.when(FuncDeclarationNode)
    def printer(self, node):
        if node.type == self.at.name:
            
            print(node.id + " : " + self.changed_methods[(node.id, self.current_type)].name)
        else:
            print(node.id + " : " + node.type)


    @visitor.when(ProgramNode)
    def visit(self, node, scope=None, type_suggested=None):
        self.changed = False
        self.errors = []
        print("entre")
        scope = Scope()
        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())
        return scope, self.errors

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope, type_suggested=None):
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
    def visit(self, node, scope, type_suggested=None):
        if scope.is_defined(node.id):
            if scope.is_local(node.id):
                error = ATTRIBUTE_OVERWRITTEN % (node.id)
            else:
                error = LOCAL_ALREADY_DEFINED % (node.id)
            self.errors.append(error)
        else:
            try:
                var_type = self.changed_atts[(node.id, self.current_type)]
            except KeyError:
                var_type = self.context.get_type(node.type)
            
            scope.define_variable(node.id, var_type, True)
            if not node.expr is None:
                expr_type = self.visit(node.expr, scope)
                if var_type.name == 'SELF_TYPE':
                    conform_type = self.current_type
                else:
                    conform_type = var_type    
                if not expr_type.conforms_to(conform_type):
                    self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, conform_type.name))
                if var_type == self.at and not expr_type == self.at:
                    self.changed_atts[(node.id, self.current_type)] = expr_type
                    self.changed = True

            try:
                self.changed_atts[(node.id, self.current_type)]
            except KeyError:
                if node.type == self.at.name:
                    print(node.id, self.current_type.name)
                    print("error autotype")
                    self.errors.append(AUTO_TYPE_ERROR % (node.id))


    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope, type_suggested=None):
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
        
        body_ret_type = self.visit(node.body, new_scope, None)
        print('Body ret type', body_ret_type.name)

        if node.type == 'void':
            return

        try:
            ret_type = self.changed_methods[(node.id, self.current_type)]
        except KeyError:
            ret_type = self.context.get_type(node.type)

        if ret_type.name == 'SELF_TYPE':
            conform_type = self.current_type
        else:
            conform_type = ret_type    

        if not body_ret_type.conforms_to(conform_type):
            self.errors.append(INCOMPATIBLE_TYPES % (body_ret_type.name, ret_type.name))
        if ret_type == self.at and not body_ret_type == self.at:
            print('Return type of body changed')
            self.changed_methods[(node.id, self.current_type)] = body_ret_type
            self.changed = True          

        try:
            self.changed_methods[(node.id, self.current_type)]
        except KeyError:
            if node.type == self.at.name:
                self.errors.append(AUTO_TYPE_ERROR % (node.id))   

        for param in node.params:
            var = new_scope.find_variable(param[0])
            if param[1] == 'AUTO_TYPE' and var.type == self.at:
                self.errors.append(AUTO_TYPE_ERROR % (param[0]))
        
        
    @visitor.when(VarDeclarationNode)
    def visit(self, node, scope, type_suggested=None):
        try:
            var_type = self.context.get_type(node.type)
        except SemanticError as error:
            self.errors.append(error.text)
            var_type = ErrorType()
            
        if scope.is_local(node.id):
            self.errors.append(LOCAL_ALREADY_DEFINED % (node.id, self.current_method.name))
        else:
            scope.define_variable(node.id, var_type)

        if not node.expr is None:
            type_expr = self.visit(node.expr, scope, None)

            if not type_expr.conforms_to(var_type):
                self.errors.append(INCOMPATIBLE_TYPES % (type_expr.name, var_type.name))
            if type_expr == self.at and var_type == self.at:
                self.errors.append(AUTO_TYPE_ERROR % (node.id))
            if var_type == self.at and not type_expr == self.at:
                node.type = type_expr.name
                return type_expr

        return var_type
            
    @visitor.when(BranchNode)
    def visit(self, node, scope, type_suggested=None):
        expr_type = self.visit(node.expr, scope, None)

        try:
            var_type = self.context.get_type(node.type)
        except:
            self.errors.append(TYPE_NOT_DEFINED % (node.type))
            var_type = ErrorType()

        if not expr_type.conforms_to(var_type):
            self.errors.append(INCOMPATIBLE_TYPES % (expr_type, var_type))
            return ErrorType()
        elif var_type == self.at and not expr_type == self.at:
            return expr_type

        return var_type

    @visitor.when(LetNode)
    def visit(self, node, scope, type_suggested=None):
        new_scope = scope.create_child()

        for attr_decl in node.attr_decl:
            self.visit(attr_decl, new_scope, None)

        return self.visit(node.body, new_scope, None)

    @visitor.when(CaseNode)
    def visit(self, node, scope, type_suggested=None):
        new_scope = scope.create_child()
        self.visit(node.expr, scope, None)

        ret_types = []
        for branch in node.branches:
            ret_types.append(self.visit(branch, new_scope, None))

        ret_type = common_ancestor(ret_types)
        if ret_type == ErrorType():
            self.errors.append('Case type error')

        return ret_type

    @visitor.when(AssignNode)
    def visit(self, node, scope, type_suggested=None):
        expr_type = self.visit(node.expr, scope, None)
        
        if not scope.is_defined(node.id):
            self.errors.append(VARIABLE_NOT_DEFINED % (node.id, self.current_method.name))
        else:
            var = scope.find_variable(node.id)
            var_type = var.type
            if not expr_type.conforms_to(var_type):
                self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, var_type.name))
            
            if var_type == self.at and not expr_type == self.at:
                if var.is_att:
                    self.changed_atts[(node.id, self.current_type)] = expr_type
                    self.changed = True
                else:
                    node.type = expr_type.name
            
        return expr_type
    
    @visitor.when(CallNode)
    def visit(self, node, scope, type_suggested=None):
        try:
            t, method = self.current_type.get_method(node.id)
            print("recuperando metodo",t.name, method.name)
        except SemanticError as e:
            self.errors.append(e)
            return ErrorType()

        call_args_types = [self.visit(arg, scope, None) for arg in node.args]
        method_args_types = [param_type for param_type in method.param_types]
        if not len(call_args_types) == len(method_args_types):
            self.errors.append(METHOD_NOT_DEFINED % (node.id, self.current_type.name))
        else:
            for i in range(len(call_args_types)):
                if not call_args_types[i].conforms_to(method_args_types[i]):
                    self.errors.append(INCOMPATIBLE_TYPES % (call_args_types[i].name, method_args_types[i].name))

        if method.return_type.name == 'SELF_TYPE':
            ret_type = self.current_type
        else:
            if method.return_type == self.at:
                try:
                    ret_type = self.changed_methods[(method.name, t)]
                except KeyError:    
                    ret_type = method.return_type
                    
        return ret_type

    @visitor.when(DispatchNode)
    def visit(self, node, scope, type_suggested=None):

        obj_type = scope.find_variable(node.obj)

        if not obj_type is None:
            obj_type = obj_type.type

        else:
            self.errors.append(VARIABLE_NOT_DEFINED % (node.obj))    
            return ErrorType()

        if obj_type == self.at:
            self.errors.append('AUTO_TYPE error at function call ' + node.id)
            return ErrorType()

        _, method = obj_type.get_method(node.id)
        if method is None:
            print('Entra a dispatch 1')
            self.errors.append(METHOD_NOT_DEFINED % (node.id, obj_type.name))
            return ErrorType()

        call_args_types = [self.visit(arg, scope, None) for arg in node.args]
        method_args_types = [param_type for param_type in method.param_types]
        if not len(call_args_types) == len(method_args_types):
            print('Entra a dispatch 2')
            self.errors.append(METHOD_NOT_DEFINED % (node.id, self.current_type.name))
        else:
            for i in range(len(call_args_types)):
                if not call_args_types[i].conforms_to(method_args_types[i]):
                    self.errors.append(INCOMPATIBLE_TYPES % (call_args_types[i].name, method_args_types[i].name))

        if method.return_type.name == 'SELF_TYPE':
            ret_type = obj_type
        else:
            ret_type = method.return_type

        try:
            type_changed = self.changed_methods[(node.id, obj_type)]
            print("siiiiii " + type_changed.name + " " + ret_type.name)
            if ret_type.name == self.at.name:
                print ("cambiando de " + ret_type.name + " a " + type_changed.name) 
                ret_type = type_changed
        except KeyError:
            pass
        print(obj_type.name, node.id)   
        print(ret_type.name)
        return ret_type

    @visitor.when(ConditionalNode)
    def visit(self, node, scope, type_suggested=None):
        pred_type = self.visit(node.pred, scope, self.context.get_type('bool'))
        then_type = self.visit(node.then_expr, scope, None)
        else_type = self.visit(node.else_expr, scope, None)

        if not pred_type.conforms_to(self.context.get_type('bool')):
            self.errors.append(INCOMPATIBLE_TYPES % (pred_type.name, 'bool'))

        print('then type', then_type.name)
        print('else type', else_type.name)
        body_type = common_ancestor([then_type, else_type])

        print('if', body_type.name)
        return body_type

    @visitor.when(LoopNode)
    def visit(self, node, scope, type_suggested=None):
        pred_type = self.visit(node.pred, scope, self.context.get_type('bool'))
        self.visit(node.body, scope, None)

        if not pred_type.conforms_to(self.context.get_type('bool')):
            self.errors.append(INCOMPATIBLE_TYPES % (pred_type.name, 'bool'))

        return self.context.get_type('void')

    @visitor.when(BinaryArithNode)
    def visit(self, node, scope, type_suggested=None):
        left_type = self.visit(node.left, scope, self.context.get_type('int'))
        right_type = self.visit(node.right, scope, self.context.get_type('int'))
        
        int_ = self.context.get_type('int')
        
        if not (right_type.conforms_to(int_) or left_type.conforms_to(int_)):
            self.errors.append(INVALID_OPERATION % (left_type.name, right_type.name))
            return ErrorType()

        return self.context.get_type('int')

    @visitor.when(MinorNode)
    def visit(self, node, scope, type_suggested=None):
        

        type_suggested = self.context.get_type('int')
        left_type = self.visit(node.left, scope, type_suggested)
        right_type = self.visit(node.right, scope, type_suggested)
        
        if not type_suggested is None and (not right_type.conforms_to(type_suggested) or not left_type.conforms_to(type_suggested)):
            self.errors.append(INVALID_OPERATION % (left_type.name, right_type.name))
            return ErrorType()

        return self.context.get_type('bool')

    @visitor.when(EqualNode)
    def visit(self, node, scope, type_suggested=None):
        
        self.visit(node.left, scope, None)
        self.visit(node.right, scope, None)
        
        return self.context.get_type('bool')    

    @visitor.when(MinorEqualNode)
    def visit(self, node, scope, type_suggested=None):
        

        type_suggested = self.context.get_type('int')
        left_type = self.visit(node.left, scope, type_suggested)
        right_type = self.visit(node.right, scope, type_suggested)
        
        if not type_suggested is None and (not right_type.conforms_to(type_suggested) or not left_type.conforms_to(type_suggested)):
            self.errors.append(INVALID_OPERATION % (left_type.name, right_type.name))
            print("El error mas al berro del mundo")
            return ErrorType()

        return self.context.get_type('bool')
    
    @visitor.when(ConstantNumNode)
    def visit(self, node, scope, type_suggested=None):
        return self.context.get_type('int')

    @visitor.when(VariableNode)
    def visit(self, node, scope, type_suggested=None):
        if not scope.is_defined(node.lex):
            self.errors.append(VARIABLE_NOT_DEFINED % (node.lex, self.current_method.name))
            return ErrorType()
        else:
            var = scope.find_variable(node.lex)
            if var.is_att and var.type == self.at:
                try:
                    current_type = self.changed_atts[(node.lex, self.current_type)]
                    return current_type
                except:
                    if not type_suggested is None:
                        self.changed_atts[(node.lex, self.current_type)] = type_suggested
                        self.changed = True
                        return type_suggested
            elif var.type == self.at:
                if not type_suggested is None:
                    var.type = type_suggested

            return var.type
            

    @visitor.when(StringNode)
    def visit(self, node, scope, type_suggested=None):
        return self.context.get_type('str')

    @visitor.when(BooleanNode)
    def visit(self, node, scope, type_suggested=None):
        return self.context.get_type('bool')

    @visitor.when(NotNode)
    def visit(self, node, scope, type_suggested=None):
        body_type = self.visit(node.lex, scope, self.context.get_type('bool'))

        if not body_type.conforms_to(self.context.get_type('bool')):
            self.errors.append(INCOMPATIBLE_TYPES % (body_type.name, 'bool'))

        return self.context.get_type('bool')

    @visitor.when(IsVoidNode)
    def visit(self, node, scope, type_suggested=None):
        self.visit(node.lex, scope, None)

        return self.context.get_type('bool')

    @visitor.when(ComplementNode)
    def visit(self, node, scope, type_suggested=None):
        body_expr = self.visit(node.lex, scope, self.context.get_type('int'))

        if not body_expr.conforms_to(self.context.get_type('int')):
            self.errors.append(INCOMPATIBLE_TYPES % (body_expr.name, 'bool'))

        return self.context.get_type('int')

    @visitor.when(SelfNode)
    def visit(self, node, scope, type_suggested=None):
        return self.current_type

    @visitor.when(InstantiateNode)
    def visit(self, node, scope, type_suggested=None):
        try:
            return self.context.get_type(node.lex)
        except SemanticError as error:
            self.errors.append(error.text)
            return ErrorType()

    
