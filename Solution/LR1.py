from cmp.automata import State, multiline_formatter
from cmp.pycompiler import Grammar
from cmp.pycompiler import Item
from cmp.utils import ContainerSet
from FirstFollow import *
from ShiftReduceParser import *
from ShiftReduceUtils import *

class LR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        
        automaton = self.build_LR1_automaton(G)

        prodOk = G.startSymbol.productions[0]
        posOk = len(prodOk.Right)
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        conflicts = []

        for node in automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    if item.production == prodOk and posOk == item.pos and G.EOF in item.lookaheads:
                        self._register(self.action, (idx, G.EOF.Name),(self.OK, 1), conflicts, node)
                        continue
                    
                    for lookahead in item.lookaheads:
                        self._register(self.action, (idx, lookahead.Name), (self.REDUCE, item.production), conflicts, node)
                        
                else:
                    if item.NextSymbol.IsTerminal:
                        self._register(self.action, (idx, item.NextSymbol.Name), (self.SHIFT, node.transitions[item.NextSymbol.Name][0].idx), conflicts, node)
                    else:
                        self._register(self.goto, (idx, item.NextSymbol.Name), (node.transitions[item.NextSymbol.Name][0].idx), conflicts, node)
        
        return automaton, conflicts

    @staticmethod
    def _register(table, key, value, conflicts, node):
        if key in table and not value in table[key]:
            if (key[1], node) not in conflicts:
                conflicts.append((key[1], node))
            table[key].append(value)
        else:
            table[key] = [value]

    def build_LR1_automaton(self, G):
        assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'
        
        firsts = compute_firsts(G)
        firsts[G.EOF] = ContainerSet(G.EOF)
        
        start_production = G.startSymbol.productions[0]
        start_item = Item(start_production, 0, lookaheads=(G.EOF,))
        start = frozenset([start_item])
        
        closure = self.closure_lr1(start, firsts)
        automaton = State(frozenset(closure), True)
        
        pending = [ start ]
        visited = { start: automaton }
        
        while pending:
            current = pending.pop()
            current_state = visited[current]
            for symbol in G.terminals + G.nonTerminals:
                closure_current = self.closure_lr1(current, firsts)
                goto = self.goto_lr1(closure_current, symbol, just_kernel=True)
                if len(goto) == 0:
                    continue
                try:
                    next_state = visited[goto]
                except KeyError:
                    next_closure = self.closure_lr1(goto, firsts)
                    visited[goto] = next_state = State(frozenset(next_closure), True)
                    pending.append(goto)

                current_state.add_transition(symbol.Name, next_state)
        
        automaton.set_formatter(multiline_formatter)
        return automaton

    def expand(self, item, firsts):
        next_symbol = item.NextSymbol
        if next_symbol is None or not next_symbol.IsNonTerminal:
            return []
        
        lookaheads = ContainerSet()
        new_items = []
        previews = item.Preview()
        for preview in previews:
            sentence = self.G.Epsilon
            for symbol in preview:
                sentence = sentence + symbol
            try:
                prev_first = firsts[sentence]
            except KeyError:
                prev_first = firsts[sentence] = compute_local_first(firsts, preview)
            
            lookaheads.update(prev_first)
            
        for prod in next_symbol.productions:
            new_item = Item(prod, 0, lookaheads = lookaheads)
            new_items.append(new_item)
        
        return new_items

    def Compact_Automata(self, automata):
        new_states = {}
        for state in automata:
            new_states[state] = state

        states_to_compress = []

        for state1 in automata:
            if not new_states[state1] == state1:
                continue
            states_to_compress = [state1] 
            for state2 in automata:
                if state1 == state2 or not new_states[state2] == state2:
                    continue
                
                node1 = state1.state
                node2 = state2.state

                are_equals = False
                if len(node1) == len(node2):
                    for item1 in node1:
                        are_equals = False
                        for item2 in node2:
                            if item1.Center() == item2.Center():
                                are_equals = True
                        if not are_equals:
                            break

                if are_equals:
                    states_to_compress.append(state2)

            compress_set = ContainerSet()

            for state in states_to_compress:
                node = state.state
                compress_set.update(ContainerSet(*node))

            new_node = self.compress(compress_set)
            new_state = State(frozenset(new_node), True)
            
            for state in states_to_compress:
                new_states[state] = new_state

        new_automata = new_states[automata]

        for state in automata:
            for key in state.transitions:
                for to_state in state.transitions[key]:
                    try:
                        assert new_states[to_state] in new_states[state].transitions[key] 
                    except:
                        new_states[state].add_transition(key, new_states[to_state])   
                        
        return new_automata

    def compress(self, items):
        centers = {}

        for item in items:
            center = item.Center()
            try:
                lookaheads = centers[center]
            except KeyError:
                centers[center] = lookaheads = set()
            lookaheads.update(item.lookaheads)
        
        return { Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items() }

    def closure_lr1(self, items, firsts):
        closure = ContainerSet(*items)
        
        changed = True
        while changed:
            changed = False
            
            new_items = ContainerSet()
            for item in closure:
                new_items.update(ContainerSet(*self.expand(item, firsts)))
            
            changed = closure.update(new_items)
            
        return self.compress(closure)

    def goto_lr1(self, items, symbol, firsts=None, just_kernel=False):
        assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
        items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
        return items if just_kernel else self.closure_lr1(items, firsts)
