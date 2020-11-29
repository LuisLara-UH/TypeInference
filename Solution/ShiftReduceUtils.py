from cmp.automata import State, lr0_formatter
from cmp.pycompiler import Item
from cmp.pycompiler import Grammar
from LL1 import ReduceNonTerminal

def build_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)

    pending = [ start_item ]
    visited = { start_item: automaton }

    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem:
            continue
            
        state = visited[current_item]
        next_item = current_item.NextItem()
        try:
            new_state = visited[next_item]
        except KeyError:
            new_state = visited[next_item] = State(next_item, True)
            pending.append(next_item)
        
        next_symbol = current_item.NextSymbol
        state.add_transition(next_symbol.Name, new_state)
        
        if next_symbol.IsNonTerminal:
            for prod in next_symbol.productions:
                item = Item(prod, 0)
                try:
                    visited[item]
                except KeyError:
                    visited[item] = State(item, True)
                    pending.append(item)
                state.add_epsilon_transition(visited[item])

        current_state = visited[current_item]
        
    return automaton

def ReverseAutomaton(automata):
    
    for node in automata:
        node.reverse_transitions = {}

    for node in automata:
        for key in node.transitions:
            for state in node.transitions[key]:
                try:
                    state.reverse_transitions[key].append(node)
                except KeyError:
                    state.reverse_transitions[key] = [node]

def FindStart(automata, state_conf, reduce_item_conflict):
    #Calcular las transiciones inversas
    ReverseAutomaton(automata)

    #Reducir el item de conflicto
    symbols_to_reduce = []
    for symbol in reduce_item_conflict.production.Right:
        symbols_to_reduce.append(symbol)

    items_way_reverse = [(reduce_item_conflict, state_conf)]
    current_state = state_conf
    current_item = reduce_item_conflict
    item_pos = current_item.pos
    while symbols_to_reduce:
        #Mover al estado anterior
        symbol = symbols_to_reduce.pop()
        current_state = current_state.reverse_transitions[symbol.Name][0]

        item_pos -= 1
        items_way_reverse.append((Item(reduce_item_conflict.production, item_pos), current_state))
    
    return items_way_reverse[::-1]

def FindConflict(start_item, automata, conflict):
    items_to_conflict_way = []

    FindWay_to_Conflict(start_item, automata, conflict, items_to_conflict_way)

    return items_to_conflict_way

def FindWay_to_Conflict(current_item, current_state, conflict, items_to_conflict_way):
    if current_item == conflict[0] and current_state == conflict[1]:
        return True
    
    if current_item.IsReduceItem:
        return False

    #Se annade el item y estado actuales al camino
    items_to_conflict_way.append((current_item, current_state))

    next_symbol = current_item.NextSymbol

    #Tratar de saltarlo
    next_item = current_item.NextItem()
    next_state = current_state.transitions[next_symbol.Name][0]

    if FindWay_to_Conflict(next_item, next_state, conflict, items_to_conflict_way):
        return True

    #Si el proximo simbolo es no-terminal
    if next_symbol.IsNonTerminal:
        #Tratar de expandirlo
        for state in current_state.state:
            try:
                item = state.state
            except:
                item = state
            if item.production.Left == next_symbol:
                next_item = item
                next_state = current_state

                if FindWay_to_Conflict(next_item, next_state, conflict, items_to_conflict_way):
                    return True

    #Se elimina el item y estado actuales al camino
    items_to_conflict_way.pop()

    return False

def FindConflictString(items_to_expand):
    #Expandir los items
    string = []
    Expand_Items(items_to_expand, 0, string)

    return string

def Expand_Items(items_to_expand, cursor, string):
    if cursor == len(items_to_expand) - 1:
        return
    
    current_item, current_state = items_to_expand[cursor]
    next_item = items_to_expand[cursor + 1][0]
    next_symbol = current_item.NextSymbol

    if next_symbol.IsTerminal:
        string.append(next_symbol)
        Expand_Items(items_to_expand, cursor + 1, string)

    else:
        if current_item.production == next_item.production:
            expanded_non_terminal = Expand_NonTerminal(current_state, next_symbol, {})
            string += expanded_non_terminal
            Expand_Items(items_to_expand, cursor + 1, string)
        else:
            Expand_Items(items_to_expand, cursor + 1, string)

            item_remainder = current_item.NextItem()
            state_remainder = current_state.transitions[next_symbol.Name][0]
            Expand_Item(item_remainder, string, state_remainder, {})

    return

def Expand_NonTerminal(current_state, NonTerminal, visited_NonTerminals):
    string = []
    visited_NonTerminals[NonTerminal] = True
    for state in current_state.state:
        item = state.state
        if item.Left == NonTerminal:
            if Expand_Item(item, string, current_state, visited_NonTerminals):
                return string
    
    visited_NonTerminals[NonTerminal] = False
    
    return None

def Expand_Item(item, string, current_state, visited_NonTerminals):
    if item.IsReduceItem:
        return True

    next_symbol = item.NextSymbol
    next_item = item.NextItem()
    next_state = current_state.transitions[next_symbol.Name][0]

    if next_symbol.IsTerminal:
        string.append(next_symbol)
        if Expand_Item(next_item, string, next_state, visited_NonTerminals):
            return True
        string.pop()

    else:
        try:
            assert visited_NonTerminals[next_symbol] == True
            return False
        except:
            Non_terminal_expanded = Expand_NonTerminal(current_state, next_symbol, visited_NonTerminals)
            if Non_terminal_expanded is None:
                return False
            
            string += Non_terminal_expanded
            if Expand_Item(next_item, string, next_state, visited_NonTerminals):
                return True
            
            for _ in Non_terminal_expanded:
                string.pop()
    
    return False
    

def Remove_Nonterminals(string, G):
    symbols = {}
    new_string = []

    for terminal in G.terminals:
        symbols[terminal.Name] = terminal

    for nonterminal in G.nonTerminals:
        symbols[nonterminal.Name] = nonterminal

    for character in string:
        symbol = symbols[character]
        if symbol.IsTerminal:
            new_string.append(symbol)
        else:
            new_string += ReduceNonTerminal(symbol)

    return new_string


        
