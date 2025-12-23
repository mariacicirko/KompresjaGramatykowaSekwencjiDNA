class SLP: # actually RLSLP
    """
    Rules:
      - For a nonterminal i, rules[i] = (a, b):
        * if a == 0: terminal rule, i -> terminal "b"
        * if a > 0: binary rule,  i -> a b   (a, b are nonterminal ids)
        * if a < 0: run rule,     i -> b^{-a}  (repeat nonterminal b -a times)
        
    Nonterminal ids are positive integers. Index 0 is unused.
    """

    def __init__(self):
        self.rules = [(0, '?')]  # rules[nt] = (a, b)
        self.lengths = [-1]       # lengths[nt] = length of expansion; -1 => unknown
        self.start = 0           # start nonterminal id (0 = empty)
        self.preterminal = {}    # terminal -> nonterminal id

    def new_nonterminal(self): # creates a fresh nonterminal id with an empty rule.
        self.rules.append((0, 0))
        self.lengths.append(-1)
        assert len(self.rules) == len(self.lengths)
        return len(self.rules) - 1

    def set_rule_terminal(self, nt, terminal): # sets nt -> terminal
        self.rules[nt] = (0, terminal)

    def set_rule_binary(self, nt, left, right): # sets nt -> left right (binary rule).
        self.rules[nt] = (left, right)
        if self.length(nt) != self.length(left) + self.length(right):
            print(f'ntb nt: {nt}({self.length(nt)}) a: {left}({self.length(left)}) b: {right}({self.length(right)})')
            exit(0)

    def new_nonterminal_binary(self, left, right): # sets nt -> left right (binary rule).
        nt = self.new_nonterminal()
        self.set_rule_binary(nt, left, right)
        return nt
    
    def set_rule_run(self, nt, base, count): # sets nt -> base^count (run-length rule). Encoded as (-count, base).
        self.rules[nt] = (-count, base)

    def get_preterminal(self, terminal): # returns (and creates if needed) a preterminal nonterminal
        if terminal in self.preterminal:
            return self.preterminal[terminal]
        nt = self.new_nonterminal()
        self.set_rule_terminal(nt, terminal)
        self.preterminal[terminal] = nt
        return nt

    def length(self, nt=None): # returns the length of Exp(nt)
        if nt is None:
            if self.start == 0:
                raise IndexError("Invalid start symbol")
            nt = self.start
        if self.lengths[nt] >= 0:
            return self.lengths[nt]
        a, b = self.rules[nt]
        if a == 0:
            self.lengths[nt] = 1
        elif a > 0: # binary
            self.lengths[nt] = self.length(a) + self.length(b)
        elif a < 0: # run
            self.lengths[nt] = (-a) * self.length(b)
        return self.lengths[nt]
    
    def access(self, index, nt=None): # returns terminal at position 'index' (0-based) by descending the derivation tree
        if nt is None:
            if self.start == 0:
                raise IndexError("Invalid start symbol")
            nt = self.start
        if index < 0 or index >= self.length(nt):
            print(f'index {index} nt: {nt} length: {self.length(nt)}')
            raise IndexError("Index out of range")
        a, b = self.rules[nt]
        if a == 0: # terminal
            return b
        elif a > 0: # binary
            if self.length(nt) != self.length(a) + self.length(b):
                print(f'nt: {nt}({self.length(nt)}) a: {a}({self.length(a)}) b: {b}({self.length(b)})')
            assert self.length(nt) == self.length(a) + self.length(b)
            if index < self.length(a):
                return self.access(index, a)
            else:
                return self.access(index - self.length(a), b)
        elif a < 0: # run
            return self.access(index % self.length(b), b)

    def size(self): # number of nonterminals (including preterminals)
        return len(self.rules) - 1

    def depth(self, nt=None): # height of the derivation (sub-)tree
        if nt is None:
            if self.start == 0:
                raise IndexError("Invalid start symbol")
            nt = self.start
        a, b = self.rules[nt]
        if a == 0: # terminal
            return 0
        if a > 0: # binary
            return max(self.depth(a), self.depth(b)) + 1
        if a < 0: # run
            return self.depth(b) + 1