from FirstFollow import *

class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    
    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self.automaton, self.conflicts = self._build_parsing_table()
    
    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        operations = []
        while True:
            state = stack[-1]
            lookahead = w[cursor]
                
            try:
                self.action[state, lookahead.Name][0]
            except:
                print(state, lookahead.Name)
                return None
                
            action, tag = self.action[state, lookahead.Name][0]
            
            if action == self.SHIFT:
                cursor -= -1
                stack.append(tag)
                operations.append('SHIFT')
                continue
                
            if action == self.REDUCE:
                if not tag.Right.IsEpsilon:
                    for i in range(len(tag.Right)):
                        stack.pop()
                new_state = stack.pop()
                stack.append(new_state)
                stack.append(self.goto[new_state, tag.Left.Name][0])
                output.append(tag)
                operations.append('REDUCE')
                continue
                
            if action == self.OK:
                return output, operations

            print(state, lookahead.Name)
            return None
