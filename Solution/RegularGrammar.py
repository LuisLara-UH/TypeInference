from automata import *

def IsRegular(G):
    for prod in G.Productions:
        if prod.IsEpsilon:
            continue
            
        if len(prod.Right) > 2:
            return False
        
        if prod.Right[0].IsNonTerminal:
            return False
        
        if len(prod.Right) == 2 and prod.Right[1].IsTerminal:
            return False
    
    return True

def ToAutomata(nonTerminals):
    states = len(nonTerminals) + 1
    finals = [states - 1]
    transitions = {}
    
    i = 0
    for nt in nonTerminals:
        nt.index = i
        i += 1
    
    for nt in nonTerminals:
        for prod in nt.productions:
            if len(prod.Right) == 2:
                try:
                    transitions[(nt.index, prod.Right[0].Name)].append(prod.Right[1].index)
                except:
                    transitions[(nt.index, prod.Right[0].Name)] = [prod.Right[1].index]
                continue
                
            if prod.IsEpsilon:
                transitions[(nt.index, '')] = [states - 1]
                continue
   
            transitions[(nt.index, prod.Right[0].Name)] = [states - 1]  
            
    return NFA(states = states, finals = finals, transitions = transitions)

def ReverseTransitions(automata):
    reverse_transitions = {}
    
    for state in range(automata.states):
        for key in automata.transitions[state]:
            transition = automata.transitions[state][key]
            for _transition in transition:
                try:
                    reverse_transitions[_transition, key].append(state)
                except KeyError:
                    reverse_transitions[_transition, key] = [state]

    return NFA(states = automata.states, finals = automata.finals, transitions = reverse_transitions).transitions

def DeleteState(automata, state, reverse_transitions):
    self_transitions = []
    for key in automata.transitions[state]:
        if state in automata.transitions[state][key]:
            self_transitions.append(key)
        
    reg_exp = ""
    if self_transitions:
        reg_exp += "("
        reg_exp += self_transitions.pop()
    
        for symbol in self_transitions:
            reg_exp += "|" + symbol
        
        reg_exp += ")*"
    
    delete_transitions = []
    add_transitions = []
    
    for key in automata.transitions[state]:

        to_state = automata.transitions[state][key]

        for _state in to_state:
            if _state == state:
                continue

            for key_reverse in reverse_transitions[state]:
                from_state = reverse_transitions[state][key_reverse]
                
                new_reg_exp = key_reverse + reg_exp + key
                
                delete_transitions.append((from_state, key_reverse, key))
                add_transitions.append((from_state, new_reg_exp, _state))
    
    for add_transition in add_transitions:
        from_state, new_reg_exp, to_state = add_transition
        for s in from_state:
            if s == state:
                continue
            try:
                automata.transitions[s][new_reg_exp].append(to_state)
            except KeyError:
                automata.transitions[s][new_reg_exp] = [to_state]

            try:
                reverse_transitions[to_state][new_reg_exp].append(s)
            except KeyError:
                reverse_transitions[to_state][new_reg_exp] = [s]
            
    for delete_transition in delete_transitions:
        from_state, key_reverse, key = delete_transition
        
        try:
            del automata.transitions[state][key]
        except KeyError:
            pass
        for s in from_state:
            try:
                automata.transitions[s][key_reverse].remove(state)
                if len(automata.transitions[s][key_reverse]) == 0:
                    del automata.transitions[s][key_reverse]
            except:
                pass

def ToRegularExpression(automata):
    for state in range(1, automata.states):
        
        reverse_transitions = ReverseTransitions(automata)
       
        DeleteState(automata, state, reverse_transitions)
       
        

    self_transitions = []
    to_final_transitions = []
    
    for key in automata.transitions[0]:
        transition = automata.transitions[0][key]
        if 0 in transition:
            self_transitions.append(key)
        if automata.states - 1 in transition:
            to_final_transitions.append(key)
    
    self_exp = ""
    if self_transitions:
        self_exp += "(" + self_transitions.pop()
        for transition in self_transitions:
            self_exp += "|" + transition
        self_exp += ")*"
        
    to_final_exp = ""
    if to_final_transitions:
        to_final_exp += "(" + to_final_transitions.pop()
        for transition in to_final_transitions:
            to_final_exp += "|" + transition
        to_final_exp += ")"
    
    return self_exp + to_final_exp