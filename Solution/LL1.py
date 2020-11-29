from FirstFollow import *
from cmp.pycompiler import *
from cmp.utils import ContainerSet
from itertools import islice

def metodo_predictivo_no_recursivo(G, M=None, firsts=None, follows=None):
    if M is None:
        if firsts is None:
            firsts = compute_firsts(G)
        if follows is None:
            follows = compute_follows(G, firsts)
        M = build_parsing_table(G, firsts, follows, [])
    
    def parser(w):
        stack = []
        stack.append(G.EOF)
        stack.append(G.startSymbol)
        cursor = 0
        output = []
        
        while True:
            top = stack.pop()
            a = w[cursor]
            if a == G.EOF and top == G.EOF:
                break
                
            if top.IsTerminal:
                if top != a:
                    return None
                cursor += 1
                    
            else:
                try:
                    production = M[top, a][0]
                except KeyError:
                    return None
                
                output.append(production)
                alpha = production.Right
                index = len(alpha) - 1
                while index >= 0:
                    stack.append(alpha[index])
                    index -= 1
        
        return output
    
    return parser

def build_parsing_table(G, firsts, follows, conflicts):
    M = {}
    bad = {}
    conf = False
    for production in G.Productions:
        X = production.Left
        alpha = production.Right
        
        for symbol in firsts[alpha]:
            if not symbol.IsEpsilon:
                try:
                    M[X, symbol].append(production)
                    
                    if not conf:
                        conflicts[0] = (X, symbol, bad[X,symbol])
                        conf = not bad[X, symbol]
                        conflicts[1] = True

                except KeyError:
                    M[X, symbol] = [production]
                    bad[X, symbol] = False
                    
        if firsts[alpha].contains_epsilon:
            for symbol in follows[X]:
                try:
                    M[X, symbol].append(production)
                
                    if not conf:
                        conflicts[0] = (X, symbol, True)
                        conflicts[1] = True
                    
                except KeyError:
                    M[X, symbol] = [production]
                    bad[X, symbol] = True
    return M

def RemoveLeftRecursive(G):
    counter = 1
    new_productions = {}
    delete_productions = []
    for symbol in G.nonTerminals:
        for prod in symbol.productions:
            if prod.Right.IsEpsilon:
                continue
                
            if symbol == prod.Right[0]:
                G.Productions.remove(prod)
                index = 2
                
                sentence = G.Epsilon

                if len(prod.Right) > 1:
                    sentence = prod.Right[1] + G.Epsilon
                    
                    
                while index < len(prod.Right):
                    sentence = sentence + prod.Right[index] + G.Epsilon
                    index += 1
                        
                delete_productions.append((symbol, prod))
                if len(sentence) >= 1:
                    try:
                        new_productions[symbol].append(sentence)
                    except KeyError:
                        new_productions[symbol] = [sentence]
                    
    for symbol, prod in delete_productions:
        symbol.productions.remove(prod)
        
    for symbol in G.nonTerminals:
        try:
            sentences = new_productions[symbol]
        except KeyError:
            continue
        
        s = 'Ex' + str(counter)
        counter += 1
        b = len(symbol.productions) != 0
        extra = G.NonTerminal(s)
        for sent in sentences:
            extra %= sent + extra + G.Epsilon
            
        extra %= G.Epsilon
        for x in symbol.productions:
            x.Right = x.Right + extra + G.Epsilon
    
    return counter  

def FindCommonPrefix(a, b):
    index = 0
    while(index < len(a) and index < len(b) and a[index] == b[index]):
        index += 1
        
    return index    

def RemoveCommonPrefixes(counter, G):
    change = True
    while change:
        change = False
        for nonTerminal in G.nonTerminals:
            if change:
                break
            for i in range(len(nonTerminal.productions)):
                if change:
                    break
                    
                for j in range(i + 1, len(nonTerminal.productions)):
                    a = nonTerminal.productions[i]
                    b = nonTerminal.productions[j]
                    	
                    if a.Right + G.Epsilon == b.Right + G.Epsilon:
                        G.Productions.remove(b)
                        nonTerminal.productions.remove(b)
                        change = True
                        break
                    else:
                        length = FindCommonPrefix(a.Right, b.Right)
                        if length > 0:
                            sentence = a.Right[0] + G.Epsilon
                            sentence1 = G.Epsilon
                            sentence2 = G.Epsilon
                            if len(a.Right) > len(b.Right):
                                mini = b
                                maxi = a
                            else:
                                mini = a
                                maxi = b
                            
                            index = 1
                            while index < length:
                                sentence = sentence + a.Right[index]
                                index += 1
                                
                            while index < len(mini.Right):
                                sentence1 = sentence1 + mini.Right[index] 
                                sentence2 = sentence2 + maxi.Right[index]
                                index += 1
                                
                            while index < len(maxi.Right):
                                sentence2 = sentence2 + maxi.Right[index]
                                index += 1
                                
                            G.Productions.remove(a)
                            G.Productions.remove(b)
                            nonTerminal.productions.remove(a)
                            nonTerminal.productions.remove(b)
                            extra = G.NonTerminal('Ex' + str(counter))
                            counter += 1
                        
                            extra %= sentence2+ G.Epsilon | sentence1+ G.Epsilon
                            nonTerminal %= sentence + extra
                            
                            
                            change = True
                            break
                        
        return counter

def compute_local_first_queue(firsts, alpha):
    first_alpha = ContainerSet()
    temp = []
    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False
        
    if alpha_is_epsilon:
        first_alpha.set_epsilon(True)
        return first_alpha
        
    breaked = False
    while len(alpha) > 0:
        symbol = alpha.pop()
        temp.append(symbol)
        first_alpha.update(firsts[symbol])
        if not firsts[symbol].contains_epsilon:
            breaked = True
            break
            
    if not breaked:
        first_alpha.set_epsilon(True)
        
    while len(temp) > 0:
        alpha.append(temp.pop())
    return first_alpha


def FindNonTerminal(form, non_terminal,productions_visited):
    temp = []
    while len(form) > 0:
    
        symbol = form.pop()
        if symbol.IsTerminal:
            temp.append(symbol)
            continue
        
        if symbol == non_terminal:
                form.append(symbol)
                length = len(temp)
                while len(temp) > 0:
                    form.append(temp.pop())
                return (True, length)
        
        #el simbolo es no terminal
        for prod in symbol.productions:
            if not prod in productions_visited:
                index = len(prod.Right) - 1
                i = index
                productions_visited.append(prod)
                while i >= 0:
                    form.append(prod.Right[i])
                    i -= 1
                boolean, length = FindNonTerminal(form, non_terminal, productions_visited)
                
                if boolean:
                    length += len(temp)
                    while len(temp) > 0:
                        form.append(temp.pop())
                    return (True, length)
                
                while index >= 0:
                    form.pop()
                    index -= 1
        
        temp.append(symbol)
    
    while len(temp) > 0:
        form.append(temp.pop())
    
    return (False, -1)

def FindNonTerminalWithFollow(form, nonTerminal, visited, terminal, firsts):
    temp = []
    
    while len(form) > 1:
        symbol = form.pop()
        if symbol.IsTerminal:
            temp.append(symbol)
            continue
        
        local_first = compute_local_first_queue(firsts, form)
        
        if symbol == nonTerminal:
            if terminal in local_first:
                position = len(temp)
                form.append(symbol)
                while len(temp) > 0:
                    form.append(temp.pop())
                
                return (True, position)    
        
        try:
            f = visited[symbol]
            if local_first in f:
                temp.append(symbol)
                continue
            visited[symbol].append(local_first)
        except KeyError:
            visited[symbol] = [local_first]
            
        for prod in symbol.productions:
            index = len(prod.Right) - 1
            i = index
            
            while i >= 0:
                form.append(prod.Right[i])
                i -= 1
            boolean, length = FindNonTerminalWithFollow(form, nonTerminal, visited, terminal, firsts)
            
            if boolean:
                length += len(temp)
                while len(temp) > 0:
                    form.append(temp.pop())
                return (True, length)
                
            while index >= 0:
                form.pop()
                index -= 1
    
        temp.append(symbol)
    
    while len(temp) > 0:
        form.append(temp.pop())
    
    return (False, -1)

def ReduceNonTerminal(nonTerminal):
    temp = [nonTerminal]
    prod_visited = []
    string = []
    while len(temp) > 0:
        symbol = temp.pop()
        
        if symbol.IsTerminal:
            string.append(symbol)
            continue
        
        for prod in nonTerminal.productions:
            if prod in prod_visited:
                continue
                
            index = len(prod.Right) - 1
            prod_visited.append(prod)
            while index >= 0:
                temp.append(prod.Right[index])
                index -= 1
                
            break
            
    return string        
        
def DoString(form, position, non_Terminal, terminal, table, G, which = 0):
    string = []
    result = 0
    count = 0
    find = False
    while len(form) > 1: #$ esta en la ultima posicion
        symbol = form.pop()
    
        if symbol.IsTerminal:
            if position == 0:
                find = True
            
            if not find:
                count += 1
                
            position -= 1    
            string.append(symbol)
            continue
        if position == 0:
            
            prod = table[non_Terminal, terminal][which]
            
            if prod.Right == G.Epsilon:
                
                position = 0
                which = 0
                non_Terminal = form.pop()
                form.append(non_Terminal)
                continue
            
            index = len(prod.Right) - 1
            while index >= 0:
                form.append(prod.Right[index])
                index -= 1
                    
            position = 1
            non_Terminal = prod.Right[0]
            
            which = 0
                
        else:
            r = ReduceNonTerminal(symbol)
            for s in r:
                string.append(s)
    
        position -= 1
        
        
    return (string, count)