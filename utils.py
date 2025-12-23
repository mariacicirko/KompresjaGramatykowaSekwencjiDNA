def binary_tree_from_sequence(slp, seq):
    """
    Given a sequence of nonterminal ids seq and an SLP object, build a balanced
    binary tree of new binary rules whose yield is exactly seq.
    Return the root nonterminal id.
    """
    n = len(seq)
    if n == 1: return seq[0]
    mid = n // 2
    a = binary_tree_from_sequence(slp, seq[:mid])
    b = binary_tree_from_sequence(slp, seq[mid:])
    root = slp.new_nonterminal()
    slp.set_rule_binary(root, a, b)
    return root
