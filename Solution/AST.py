class Node:
    pass

class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations

class DeclarationNode(Node):
    pass

class ExpressionNode(Node):
    pass

class ClassDeclarationNode(DeclarationNode):
    def __init__(self, idx, features, parent=None):
        self.id = idx
        self.parent = parent
        self.features = features

class FuncDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, return_type, body):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body

class AttrDeclarationNode(DeclarationNode):
    def __init__(self, idx, typex, expr=None):
        self.id = idx
        self.type = typex
        self.expr = expr

class VarDeclarationNode(ExpressionNode):
    def __init__(self, idx, typex, expr=None):
        self.id = idx
        self.type = typex
        self.expr = expr

class BranchNode(ExpressionNode):
    def __init__(self, idx, typex, expr):
        self.id = idx
        self.type = typex
        self.expr = expr

class BlockNode(ExpressionNode):
    def __init__(self, expr_list):
        self.expr_list = expr_list

class LetNode(ExpressionNode):
    def __init__(self, attr_decl, body):
        self.attr_decl = attr_decl
        self.body = body

class CaseNode(ExpressionNode):
    def __init__(self, expr, branches):
        self.expr = expr
        self.branches = branches

class AssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr

class CallNode(ExpressionNode):
    def __init__(self, idx, args):
        self.id = idx
        self.args = args

class DispatchNode(ExpressionNode):
    def __init__(self, obj, idx, args, dispatch_type=None):
        self.obj = obj
        self.id = idx
        self.args = args
        self.dispatch_type = dispatch_type

class ConditionalNode(ExpressionNode):
    def __init__(self, predicate, then_expr, else_expr):
        self.pred = predicate
        self.then_expr = then_expr
        self.else_expr = else_expr

class LoopNode(ExpressionNode):
    def __init__(self, predicate, body):
        self.pred = predicate
        self.body = body

class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        self.lex = lex

class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class ConstantNumNode(AtomicNode):
    pass
class VariableNode(AtomicNode):
    pass
class StringNode(AtomicNode):
    pass
class BooleanNode(AtomicNode):
    pass
class NotNode(AtomicNode):
    pass
class IsVoidNode(AtomicNode):
    pass
class ComplementNode(AtomicNode):
    pass
class SelfNode(AtomicNode):
    pass
class InstantiateNode(AtomicNode):
    pass

class BinaryBooleanNode(BinaryNode):
    pass

class BinaryArithNode(BinaryNode):
    pass

class PlusNode(BinaryArithNode):
    pass
class MinusNode(BinaryArithNode):
    pass
class StarNode(BinaryArithNode):
    pass
class DivNode(BinaryArithNode):
    pass
class MinorNode(BinaryBooleanNode):
    pass
class MinorEqualNode(BinaryBooleanNode):
    pass
class EqualNode(BinaryBooleanNode):
    pass
