from slp import SLP
from utils import binary_tree_from_sequence

def compress_repair(text):
    """
    Simple RePair-style grammar compressor using the SLP structure.
    Produces a pure CNF SLP (no run rules).
    """
    slp = SLP()
    sequence = [slp.get_preterminal(ch) for ch in text]

    while True:
        if len(sequence) < 2:
            break

        # count bi-gram frequencies
        pair_freq = {}
        n = len(sequence)
        for i in range(n - 1):
            pair = (sequence[i], sequence[i + 1])
            if pair not in pair_freq:
                pair_freq[pair] = 0
            pair_freq[pair] += 1

        # find most frequent pair
        best_pair = None
        for pair, count in pair_freq.items():
            if best_pair is None or count > pair_freq[best_pair]:
                best_pair = pair

        # if there are no repetitive pairs, build a naive balanced tree
        if best_pair is None or pair_freq[best_pair] < 2:
            break

        # print(f'seq: {sequence}')
        # print(f'best pair: {best_pair}')

        # compose a production X -> A B
        A, B = best_pair
        X = slp.new_nonterminal()
        slp.set_rule_binary(X, A, B)

        # replace all non-overlapping occurrences of (A B)
        new_seq = []
        i = 0
        n = len(sequence)
        while i < n:
            if i < n - 1 and sequence[i] == A and sequence[i + 1] == B:
                new_seq.append(X)
                i += 2
            else:
                new_seq.append(sequence[i])
                i += 1
        sequence = new_seq

    # final start symbol
    if len(sequence) == 1:
        slp.start = sequence[0]
    else:
        # print(f'naive for: {sequence}')
        slp.start = binary_tree_from_sequence(slp, sequence)

    return slp