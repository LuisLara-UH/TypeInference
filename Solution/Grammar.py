from cmp.pycompiler import Grammar
from AST import *

def get_grammar():
    # grammar
    G = Grammar()

    # non-terminals
    program = G.NonTerminal('<program>', startSymbol=True)
    class_list, def_class = G.NonTerminals('<class-list> <def-class>')
    feature_list, def_attr, def_func = G.NonTerminals('<feature-list> <def-attr> <def-func>')
    param_list, param, expr_list = G.NonTerminals('<param-list> <param> <expr-list>')
    expr, arith, term, atom = G.NonTerminals('<expr> <arith> <term> <atom>')
    func_call, arg_list, param_list_formal  = G.NonTerminals('<func-call> <arg-list> <param-list-formal>')
    if_expr, while_expr, block, let_expr, case_expr  = G.NonTerminals('<if-expr> <while_expr> <block> <let-expr> <case-expr>')
    var_decl, let_att, case_body, arg_list_formal = G.NonTerminals('<var-decl> <let-att> <case-body> <arg-list-formal>')

    # terminals
    classx, let, _in = G.Terminals('class let in')
    semi, colon, comma, dot, opar, cpar, ocur, ccur, at = G.Terminals('; : , . ( ) { } @')
    equal, plus, minus, star, div = G.Terminals('= + - * /')
    idx, num, string, new, _self = G.Terminals('id int string new self')
    inheritsx, left_arrow, right_arrow, _not, isvoid, complement = G.Terminals('inherits <- => not isvoid ~')
    minor, minor_eq, true, false = G.Terminals('< <= true false')
    _if, fi, _else, then = G.Terminals('if fi else then')
    _while, loop, pool = G.Terminals('while loop pool')
    case, of, esac, double_quote = G.Terminals('case of esac "')

    # productions
    program %= class_list, lambda h,s: ProgramNode(s[1])

    # <class-list>
    class_list %= def_class + semi, lambda h,s: [ s[1] ]
    class_list %= def_class + semi + class_list, lambda h,s: [ s[1] ] + s[3]

    # <def-class>
    def_class %= classx + idx + ocur + feature_list + ccur, lambda h,s: ClassDeclarationNode(s[2], s[4])
    def_class %= classx + idx + inheritsx + idx + ocur + feature_list + ccur, lambda h,s: ClassDeclarationNode(s[2], s[6], s[4])

    # <feature-list>
    feature_list %= G.Epsilon, lambda h,s: [ ]
    feature_list %= def_attr + semi + feature_list, lambda h,s: [ s[1] ] + s[3]
    feature_list %= def_func + semi + feature_list, lambda h,s: [ s[1] ] + s[3]

    # <def-attr>
    def_attr %= idx + colon + idx, lambda h,s: AttrDeclarationNode(s[1], s[3])
    def_attr %= idx + colon + idx + left_arrow + expr, lambda h,s: AttrDeclarationNode(s[1], s[3], s[5])

    # <def-func>
    def_func %= idx + opar + param_list + cpar + colon + idx + ocur + expr + ccur, lambda h,s: FuncDeclarationNode(s[1], s[3], s[6], s[8])

    # <param-list>
    param_list %= param_list_formal, lambda h,s:  s[1]
    param_list %= G.Epsilon, lambda h,s: []

    # <param-list-formal>
    param_list_formal %= param, lambda h,s: [ s[1] ]
    param_list_formal %= param + comma + param_list_formal, lambda h,s: [ s[1] ] + s[3]

    # <param>
    param %= idx + colon + idx, lambda h,s: [s[1], s[3]]

    # <expr>         
    expr %= arith, lambda h,s: s[1]

    expr %= expr + minor + arith, lambda h,s: MinorNode(s[1], s[3])
    expr %= expr + minor_eq + arith, lambda h,s: MinorEqualNode(s[1], s[3])
    expr %= expr + equal + arith, lambda h,s: EqualNode(s[1], s[3])

    # <arith>        
    arith %= term, lambda h,s: s[1]
    arith %= arith + plus + term, lambda h,s: PlusNode(s[1], s[3])
    arith %= arith + minus + term, lambda h,s: MinusNode(s[1], s[3])

    # <term>         
    term %= atom, lambda h,s: s[1] 
    term %= term + star + atom, lambda h,s: StarNode(s[1], s[3])
    term %= term + div + atom, lambda h,s: DivNode(s[1], s[3])

    # <atom>         
    atom %= idx, lambda h,s: VariableNode(s[1])
    atom %= num, lambda h,s: ConstantNumNode(s[1])
    atom %= string, lambda h,s: StringNode(s[1])
    atom %= _self, lambda h,s: SelfNode(s[1])

    atom %= true, lambda h,s: BooleanNode(s[1])
    atom %= false, lambda h,s: BooleanNode(s[1])

    atom %= opar + expr + cpar, lambda h,s: s[2] #####

    #atom %= _not + atom, lambda h,s: NotNode(s[2])
    
    atom %= func_call, lambda h,s: s[1]
    
    atom %= new + idx, lambda h,s: InstantiateNode(s[2])
    #atom %= isvoid + atom, lambda h,s: IsVoidNode(s[2])
    #atom %= complement + atom, lambda h,s: ComplementNode(s[2])
    
    atom %= idx + left_arrow + atom, lambda h,s: AssignNode(s[1], s[3])
    
    atom %= if_expr, lambda h,s: s[1]
    #atom %= while_expr, lambda h,s: s[1]
    #atom %= block, lambda h,s: s[1]
    #atom %= let_expr, lambda h,s: s[1]
    #atom %= case_expr, lambda h,s: s[1]
    
    # <if-expr>
    if_expr %= _if + expr + then + expr + _else + expr + fi, lambda h,s: ConditionalNode(s[2], s[4], s[6])

    # <while-expr>
    #while_expr %= _while + expr + loop + expr + pool, lambda h,s: LoopNode(s[2], s[4])

    # <block>
    #block %= ocur + expr_list + ccur, lambda h,s: s[2]
    
    # <let-expr>
    #let_expr %= let + let_att + _in + atom, lambda h,s: LetNode(s[2], s[4])

    # <let-att>
    #let_att %= var_decl, lambda h,s: [ s[1] ]
    #let_att %= var_decl + comma + let_att, lambda h,s: [ s[1] ] + s[3]

    # <var-decl>
    #var_decl %= idx + colon + idx, lambda h,s: VarDeclarationNode(s[1], s[3])
    #var_decl %= idx + colon + idx + left_arrow + expr, lambda h,s: VarDeclarationNode(s[1], s[3], s[5])
    
    # <case-expr>
    #case_expr %= case + expr + of + case_body + esac, lambda h,s: CaseNode(s[2], s[4])

    # <case-body>
    #case_body %= idx + colon + idx + right_arrow + expr + semi, lambda h,s: [ BranchNode(s[1], s[3], s[5]) ]
    #case_body %= idx + colon + idx + right_arrow + expr + semi + case_body, lambda h,s: [ BranchNode(s[1], s[3], s[5]) ] + s[7]

    # <expr-list>
    expr_list %= expr + semi, lambda h,s: [ s[1] ]
    expr_list %= expr + semi + expr_list, lambda h,s: [ s[1] ] + s[3]

    # <func-call>    
    func_call %= idx + opar + arg_list + cpar, lambda h,s: CallNode(s[1], s[3])
    func_call %= idx + dot + idx + opar + arg_list + cpar, lambda h,s: DispatchNode(s[1], s[3], s[5])
    #func_call %= opar + expr + cpar + dot + idx + opar + arg_list + cpar, lambda h,s: DispatchNode(s[2], s[5], s[7])
    #func_call %= idx + at + idx + dot + idx + opar + arg_list + cpar, lambda h,s: DispatchNode(s[1], s[5], s[7], s[3])
    #func_call %= opar + expr + cpar + at + idx + dot + idx + opar + arg_list + cpar, lambda h,s: DispatchNode(s[2], s[7], s[9], s[5])
    #func_call %= func_call + dot + idx + opar + arg_list + cpar, lambda h,s: DispatchNode(s[1], s[3], s[5])
    #func_call %= func_call + at + idx + dot + idx + opar + arg_list + cpar, lambda h,s: DispatchNode(s[1], s[5], s[7], s[3])
    
    # <arg-list>
    arg_list %= G.Epsilon, lambda h,s: []
    arg_list %= arg_list_formal, lambda h,s: s[1]

    # <arg-list-formal>
    arg_list_formal %= expr, lambda h,s: [ s[1] ]
    arg_list_formal %= expr + comma + arg_list_formal, lambda h,s: [ s[1] ] + s[3]
    
    return G, idx, num, string, ocur, ccur, semi