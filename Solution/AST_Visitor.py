import cmp.visitor as visitor
from AST import *

class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ProgramNode [<class> ... <class>]'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.declarations)
        return f'{ans}\n{statements}'
    
    @visitor.when(ClassDeclarationNode)
    def visit(self, node, tabs=0):
        parent = '' if node.parent is None else f": {node.parent}"
        ans = '\t' * tabs + f'\\__ClassDeclarationNode: class {node.id} {parent} {{ <feature> ... <feature> }}'
        features = '\n'.join(self.visit(child, tabs + 1) for child in node.features)
        return f'{ans}\n{features}'
    
    @visitor.when(AttrDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AttrDeclarationNode: {node.id} : {node.type}'
        return f'{ans}'
    
    @visitor.when(VarDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__VarDeclarationNode: let {node.id} : {node.type} = <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'
    
    @visitor.when(BranchNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__BranchNode: {node.id} : {node.type} => <exp>;'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(LetNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__LetNode: let <var-decl>, ... , <var-decl> in <atom>'
        let_att = '\n'.join(self.visit(att, tabs + 1) for att in node.attr_decl)
        return f'{ans}\n{let_att}'


    @visitor.when(CaseNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__CaseNode: case <exp> of <branch>; ... ; <branch> esac'
        case_body = '\n'.join(self.visit(branch, tabs + 1) for att in node.branches)
        return f'{ans}\n{case_body}'

    @visitor.when(AssignNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AssignNode: let {node.id} = <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'
    
    @visitor.when(FuncDeclarationNode)
    def visit(self, node, tabs=0):
        print(node.params)
        params = ', '.join(f'{param[0]} : {param[1]}' for param in node.params)
        ans = '\t' * tabs + f'\\__FuncDeclarationNode: def {node.id}({params}) : {node.type} -> <body>'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(BinaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(AtomicNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.lex}'
    
    @visitor.when(CallNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__CallNode: <obj>.{node.id}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{args}'

    @visitor.when(DispatchNode)
    def visit(self, node, tabs=0):
        if node.dispatch_type is None:
            ans = '\t' * tabs + f'\\__CallNode: <obj>.{node.id}(<expr>, ..., <expr>)'
        else:
            ans = '\t' * tabs + f'\\__CallNode: <obj>.{node.id}@{node.dispatch_type}(<expr>, ..., <expr>)'
        obj = self.visit(node.obj, tabs + 1)
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)

        return f'{ans}\n{obj}\n{args}'

    @visitor.when(ConditionalNode)
    def visit(self, node, tabs=0):
        ans = '/t' * tabs + f'\\__ConditionalNode: if <exp> then <exp> else <exp> fi'
        predicate = self.visit(node.pred, tabs + 1)
        then = self.visit(node.then_expr, tabs + 1)
        _else = self.visit(node.else_expr, tabs + 1)

        return f'{ans}\n{predicate}\n{then}\n{_else}'

    @visitor.when(LoopNode)
    def visit(self, node, tabs=0):
        ans = '/t' * tabs + f'\\__LoopNode: while <exp> loop <exp> pool'
        predicate = self.visit(node.pred, tabs + 1)
        loop = self.visit(node.body, tabs + 1)

        return f'{ans}\n{predicate}\n{loop}'
    
    @visitor.when(InstantiateNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ InstantiateNode: new {node.lex}'