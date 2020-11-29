from cmp.utils import ContainerSet
import pydot

class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')
        
    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()
            
    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else ''))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else ''))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass

class DFA(NFA):
    
    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)
        transitions = { key: [value] for key, value in transitions.items() }
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start
        
    def _move(self, symbol):
        try:
            self.current = self.transitions[self.current][symbol][0]
            return True
        except KeyError:
            return False
        
    
    def _reset(self):
        self.current = self.start
        
    def recognize(self, string):
        index = 0
        while index < len(string) and self._move(string[index]):
            index += 1
        
        
        
        if index == len(string) and self.current in self.finals:
            self._reset()
            return True
        
        self._reset()
        return False

def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            for t in automaton.transitions[state][symbol]:
                moves.add(t)
                
        except KeyError:
            continue
    return moves

def epsilon_closure(automaton, states):
    pending = [ s for s in states ] 
    closure = { s for s in states } 
    
    while pending:
        state = pending.pop()
        try:
            t_states = automaton.transitions[state]['']
            for s in t_states:
                if not s in closure:
                    closure.add(s)
                    pending.append(s)
                    
        except KeyError:
            continue
            
    return ContainerSet(*closure)

def nfa_to_dfa(automaton):
    transitions = {}
    
    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [ start ]
    counter = 1

    pending = [ start ]
    while pending:
        state = pending.pop()
        
        for symbol in automaton.vocabulary:
            goto = move(automaton, state, symbol)
            if goto == set():
                continue
            goto = epsilon_closure(automaton, goto)
            
            was = False
            for s in states:
                if goto == s:
                    goto = s
                    was = True
            
            if not was:
                goto.id = counter
                counter += 1
                goto.is_final = any(s in automaton.finals for s in goto)
                states.append(goto)
                pending.append(goto)
             
            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:
                transitions[state.id, symbol] = goto.id
    
    finals = [ state.id for state in states if state.is_final ]
    dfa = DFA(len(states), finals, transitions)
    return dfa