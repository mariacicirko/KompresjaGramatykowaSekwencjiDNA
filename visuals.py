from slp import SLP
from repair import compress_repair
from tests import repair_adversary
from balancing import get_heavy_paths, get_longest_path, balance, balance_longest_path

from collections import defaultdict

res = '\\documentclass{standalone}\n\\usepackage{tikz}\n\\begin{document}\n\\begin{tikzpicture}'
res += '[x=1.5em, y=3em, inner node/.style={circle, draw=black, fill=white, thick, inner sep=1.9pt}, leaf/.style={}, light edge/.style={-{Stealth}, semithick}, heavy edge/.style={light edge, red}]'
res += '\\usetikzlibrary{arrows.meta}'

edge_styles = defaultdict(lambda: 'light edge')
node_styles = defaultdict(lambda: 'inner node')

def dfs(G, u=None, span=None, current_id=0):
    global res
    id = current_id
    if u is None:
        u = G.start
        span = (0, G.length())
    a, b = G.rules[u]
    if a == 0: # terminal
        x_0, x_1 = span
        assert x_1 == x_0 + 1
        position = (x_0 + x_1) / 2
        res += f'\\node[leaf] ({id}) at ({position},0) {{\\texttt{{{b}}}}};'
        return (0, id)
    elif a > 0: # binary
        x_0, x_1 = span
        cut = x_0 + G.length(a)
        depth_a, id_a = dfs(G, a, span=(x_0, cut), current_id=id + 1)
        depth_b, id_b = dfs(G, b, span=(cut, x_1), current_id=id_a + 1)
        depth = max(depth_a, depth_b) + 1
        position = cut
        res += f'\\node[{node_styles[u]}] ({id}) at ({position},{depth}) {{{u}}};'
        res += f'\\draw[{edge_styles[(u, a)]}] ({id}) -- ({id_a});'
        res += f'\\draw[{edge_styles[(u, b)]}] ({id}) -- ({id_b});'
        return depth, id


def show_longest_path(G):
    P, L, R = get_longest_path(G)
    for i in range(len(P) - 1):
        edge_styles[(P[i], P[i + 1])] = 'heavy edge'
        edge_styles[(P[i], L[i])] = 'light edge, blue'
        edge_styles[(P[i], R[i])] = 'light edge, blue'


def show_longest_path_balancing(G):
    n_init = G.size()
    balance_longest_path(G)
    n = G.size()
    for i in range(n_init + 1, n):
        node_styles[i] = 'inner node, draw=green'


def show_heavy_path_balancing(G):
    n_init = G.size()
    balance(G)
    n = G.size()
    for i in range(n_init + 1, n):
        node_styles[i] = 'inner node, draw=green'


def show_heavy_paths(G):
    heavy_paths = get_heavy_paths(G)
    for P, L, R in heavy_paths:
        if len(P) <= 2: continue
        for i in range(len(P) - 1):
            edge_styles[(P[i], P[i + 1])] = 'heavy edge'
            edge_styles[(P[i], L[i])] = 'light edge, blue'
            edge_styles[(P[i], R[i])] = 'light edge, blue'
    

def draw_derivation_tree(G):
    global res
    depth, root_id = dfs(G)
    assert depth == G.depth()
    # res += f'\\node[align=left, anchor=west] at ({0},{depth}) {{depth: ${depth}$ \\\\ size: ${G.size()}$}};'
    res += '\\end{tikzpicture}\n\\end{document}'
    print(res)


if __name__ == '__main__':
    s = repair_adversary(18, random_extension_side=True, random_block_order=True, seed=1)
    
    G = compress_repair(s)
    
    # show_longest_path(G)
    # show_longest_path_balancing(G)
    
    # show_heavy_paths(G)
    show_heavy_path_balancing(G)
    
    draw_derivation_tree(G)
    