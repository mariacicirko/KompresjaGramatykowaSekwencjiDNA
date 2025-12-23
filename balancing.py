from slp import SLP
from repair import compress_repair
from tests import repair_adversary

from copy import copy


def make_shortcuts(G, s, reverse_result=False):
    """
    Slow implementation of Proposition 2.3. 
    
    Input:
    * grammar G
    * list of nonterminals / weighted string s, with possible None entries
    * whether the concatenations should be swapped at all places
    
    Output: new nonterminals producing all suffixes of U are added to G; returns their list
    
    The notation is (mostly) consistent with the paper, with some auxiliary variables
    """
    
    def new_production(A, B):
        if reverse_result:
            return G.new_nonterminal_binary(B, A)
        else:
            return G.new_nonterminal_binary(A, B)
    
    if sum([(x is not None) for x in s]) <= 1: return s # if there is ≤ 1 character, return s
    
    total = sum([G.length(x) for x in s if x is not None]) # total weight/length of s

    k = len(s) - 1
    w = G.length(s[k]) if s[k] is not None else 0
    while w.bit_length() < total.bit_length():
        k -= 1
        w += G.length(s[k]) if s[k] is not None else 0
    
    assert s[k] != None
    
    # split into two parts
    a = s[ : k]
    b = s[k + 1 : ]
    
    # shrink the left part by merging consecutive pairs, for linear convergence
    X = copy(a)
    last = None
    for i in range(len(X)):
        if X[i] is not None:
            if last is None:
                last = i
            else:
                X[last] = new_production(X[last], X[i])
                X[i] = None
                last = None
    
    U = make_shortcuts(G, X, reverse_result)
    V = make_shortcuts(G, b, reverse_result)
    
    C = s[k] # nonterminal for suffix starting at k
    for u in V:
        if u is not None:
            C = new_production(C, u)
            break
        
    last = None
    for i in reversed(range(len(U))):
        if a[i] is None:
            assert X[i] is None and U[i] is None
            continue
        if X[i] is not None:
            assert U[i] is not None
            U[i] = new_production(U[i], C)
            last = U[i]
            continue
        assert U[i] is None
        if last is not None:
            U[i] = new_production(a[i], last)
        else:
            U[i] = new_production(a[i], C)
            
    return U + [C] + V


def count_paths_from_root(G): # counts paths from the root to every nonterminal
    n = len(G.rules)
    assert G.start == n - 1, ('nonterminals not topologically sorted')
    G.paths_from_root = [0 for i in range(n)]
    G.paths_from_root[n - 1] = 1
    for i in reversed(range(1, n)):
        a, b = G.rules[i]
        if a == 0: continue
        assert a < i and b < i, ('nonterminals not topologically sorted')
        G.paths_from_root[a] += G.paths_from_root[i]
        G.paths_from_root[b] += G.paths_from_root[i]


def descend_heavy_path(G, u):
    a, b = G.rules[u]
    if a == 0: return [u], [], [] # u is a leaf
    # edge is heavy iff the floors of log_2 are equal for paths_from_root and equal for paths_to_leaves
    # returns the heavy path starting at u, the left neighbors, and the right neighbors
    sig_u = (G.paths_from_root[u].bit_length(), G.length(u).bit_length()) 
    sig_a = (G.paths_from_root[a].bit_length(), G.length(a).bit_length())
    sig_b = (G.paths_from_root[b].bit_length(), G.length(b).bit_length())
    if sig_u == sig_a:
        assert sig_u != sig_b # both children cannot be heavy
        P, L, R = descend_heavy_path(G, a)
        P.append(u)
        L.append(None)
        R.append(b)
        return P, L, R
    if sig_u == sig_b:
        assert sig_u != sig_a # both children cannot be heavy
        P, L, R = descend_heavy_path(G, b)
        P.append(u)
        L.append(a)
        R.append(None)
        return P, L, R
    return [u], [], []


def get_heavy_paths(G):
    count_paths_from_root(G)
    n = len(G.rules)
    visited = [False for i in range(n)]
    heavy_paths = []
    for i in reversed(range(1, n)):
        if visited[i] == True: continue
        P, L, R = descend_heavy_path(G, i)
        P.reverse()
        L.reverse()
        R.reverse()
        for x in P: visited[x] = True
        heavy_paths.append((P, L, R))
    G.paths_from_root = None
    return heavy_paths


def balance_path(G, P, L, R):
    if len(P) <= 2: return
    L_suff = make_shortcuts(G, L, reverse_result=False)
    R_suff = make_shortcuts(G, R, reverse_result=True)
    
    for i in reversed(range(len(L) - 1)):
        if L[i] is None:
            assert L_suff[i] is None
            L_suff[i] = L_suff[i + 1]
        
    for i in reversed(range(len(R) - 1)):
        if R[i] is None:
            assert R_suff[i] is None
            R_suff[i] = R_suff[i + 1]       
    
    for i in range(len(P) - 1):
        assert L_suff[i] is not None or R_suff[i] is not None
        if L_suff[i] is not None and R_suff[i] is None:
            G.set_rule_binary(P[i], L_suff[i], P[-1])
        if L_suff[i] is None and R_suff[i] is not None:
            G.set_rule_binary(P[i], P[-1], R_suff[i])
        if L_suff[i] is not None and R_suff[i] is not None:
            X = G.new_nonterminal_binary(L_suff[i], P[-1])
            G.set_rule_binary(P[i], X, R_suff[i])


def balance(G):
    """
    Input: SLP G producing s of length |s| = n
    Output: Modifies G (in place), makes it O(log n) depth
    
    Algorithm inspired by Theorem 1.2 from Balancing Straight-Line Programs by Moses Ganardi, Artur Jeż, and Markus Lohrey (FOCS 2019)

    * Assume that for all productions X -> A B we have A, B < X (on ids)
    * Assume that each nonterminal is reachable from the root
    
    """
    heavy_paths = get_heavy_paths(G)
    for P, L, R in heavy_paths:
        balance_path(G, P, L, R)
    return G


def get_longest_path(G, u=None):
    if u is None: u = G.start
    assert u != 0
    a, b = G.rules[u]
    if a == 0: return [u], [], []
    Pa, La, Ra = get_longest_path(G, a)
    Pb, Lb, Rb = get_longest_path(G, b)
    if len(Pa) >= len(Pb):
        return [u] + Pa, [None] + La, [b] + Ra
    else:
        return [u] + Pb, [a] + Lb, [None] + Rb


def balance_longest_path(G):
    P, L, R = get_longest_path(G)
    balance_path(G, P, L, R)
    return G
                
if __name__ == "__main__":
    s = repair_adversary(12, random_extension_side=True, random_block_order=True)
    G = compress_repair(s)
    
    print(f'length: {G.length()}    size: {G.size()}    depth: {G.depth()}')
    
    balance_longest_path(G)
    # balance(G)
    
    print(f'length: {G.length()}    size: {G.size()}    depth: {G.depth()}')
    
    # t = [G.access(i) for i in range(G.length())]
    # for i in range(len(s)):
    #     if s[i] != t[i]:
    #         print(f'mismatch at position {i}')
            
    # assert s == t