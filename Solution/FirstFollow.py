from cmp.pycompiler import *
from cmp.utils import ContainerSet
from itertools import islice

def compute_local_first(firsts, alpha):
    first_alpha = ContainerSet()
    
    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False
        
    if alpha_is_epsilon:
        first_alpha.set_epsilon(True)
        return first_alpha
        
    breaked = False
    for symbol in alpha:#for symbol in alpha._symbols:
        first_alpha.update(firsts[symbol])
        if not firsts[symbol].contains_epsilon:
            breaked = True
            break
            
    if not breaked:
        first_alpha.set_epsilon(True)
        
    return first_alpha

def compute_firsts(G):
    firsts = {}
    change = True
    
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)
        
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()
    
    while change:
        change = False
        
        for production in G.Productions:
            X = production.Left
            alpha = production.Right + G.Epsilon
            
            first_X = firsts[X]
                
            try:
                first_alpha = firsts[alpha]
            except:
                first_alpha = firsts[alpha] = ContainerSet()
            
            local_first = compute_local_first(firsts, alpha)
            
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)
                    
    return firsts

from itertools import islice

def compute_follows(G, firsts):
    follows = { }
    change = True
    
    local_firsts = {}
    
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    follows[G.startSymbol] = ContainerSet(G.EOF)
    
    while change:
        change = False
        
        for production in G.Productions:
            X = production.Left
            alpha = production.Right + G.Epsilon
            
            follow_X = follows[X]
            
            if alpha.IsEpsilon:
                continue
                
            n = len(alpha) - 1
            if alpha[n].IsNonTerminal:
                change |= follows[alpha[n]].update(follow_X)
            
            n-=1
            first_epsilon = True
            while n >= 0:
                if alpha[n].IsNonTerminal:
                        if alpha[n + 1].IsNonTerminal:
                            first_epsilon = first_epsilon and firsts[alpha[n + 1]].contains_epsilon
                            if first_epsilon:
                                change |= follows[alpha[n]].update(follow_X)
                                
                            change |= follows[alpha[n]].update(firsts[alpha[n + 1]])

                            i = n + 1
                            while i < len(alpha) - 1 and (G.Epsilon in firsts[alpha[i]]):
                                i += 1
                                change |= follows[alpha[n]].update(firsts[alpha[i]])
                            
                        else:
                            change |= follows[alpha[n]].update(ContainerSet(alpha[n + 1]))
                            
                        
                n-=1

    return follows