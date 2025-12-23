from slp import SLP
from utils import binary_tree_from_sequence
import random


def compress_recompression(text, seed=123):
    """
    Recompression-style SLP with run rules (RLSLP):
      - start from terminals for each character,
      - repeatedly:
          1) block compression: compress maximal runs X^k into run rules,
          2) pair compression: random partition of symbols into 0/1 and
             compress all 0-1 pairs into binary rules.
      - fall back to greedy left-to-right pairing if an iteration makes no progress.
    """
    rng = random.Random(seed)
    slp = SLP()
    seq = [slp.get_preterminal(ch) for ch in text]

    while len(seq) > 1:
        changed = False

        # block compression (runs)
        new_seq = []
        i = 0
        n = len(seq)
        while i < n:
            j = i + 1
            while j < n and seq[j] == seq[i]:
                j += 1
            run_len = j - i
            if run_len >= 2:
                base = seq[i]
                nt = slp.new_nonterminal()
                slp.set_rule_run(nt, base, run_len)
                new_seq.append(nt)
                changed = True
            else:
                new_seq.append(seq[i])
            i = j
        seq = new_seq

        if len(seq) <= 1:
            break

        # pair compression with random partition
        distinct = set(seq)
        symbol_to_bit = {sym: rng.randint(0, 1) for sym in distinct}

        new_seq = []
        pair_nt = {}
        i = 0
        n = len(seq)
        while i < n:
            if i < n - 1:
                a_sym = seq[i]
                b_sym = seq[i + 1]
                if symbol_to_bit[a_sym] == 0 and symbol_to_bit[b_sym] == 1:
                    pair = (a_sym, b_sym)
                    if pair in pair_nt:
                        nt = pair_nt[pair]
                    else:
                        nt = slp.new_nonterminal()
                        slp.set_rule_binary(nt, a_sym, b_sym)
                        pair_nt[pair] = nt
                    new_seq.append(nt)
                    changed = True
                    i += 2
                    continue
            new_seq.append(seq[i])
            i += 1
        seq = new_seq

        # fallback if nothing changed
        if not changed:
            if len(seq) <= 1:
                break
            new_seq = []
            pair_nt = {}
            i = 0
            n = len(seq)
            while i < n:
                if i < n - 1:
                    a_sym = seq[i]
                    b_sym = seq[i + 1]
                    pair = (a_sym, b_sym)
                    if pair in pair_nt:
                        nt = pair_nt[pair]
                    else:
                        nt = slp.new_nonterminal()
                        slp.set_rule_binary(nt, a_sym, b_sym)
                        pair_nt[pair] = nt
                    new_seq.append(nt)
                    i += 2
                else:
                    new_seq.append(seq[i])
                    i += 1
            seq = new_seq

    if len(seq) == 1:
        slp.start = seq[0]
    else:
        slp.start = binary_tree_from_sequence(slp, seq)

    return slp


def _compute_greedy_bits_for_sequence(seq):
    """
    Determine a deterministic 0/1 assignment for each symbol in seq
    in order to greedily increase the number of 0-1 pairs.
    """
    pair_freq = {}
    n = len(seq)
    for i in range(n - 1):
        pair = (seq[i], seq[i + 1])
        pair_freq[pair] = pair_freq.get(pair, 0) + 1

    symbols = set(seq)
    items = list(pair_freq.items())

    def pair_key(item):
        (a, b), cnt = item
        return (-cnt, a, b)

    items.sort(key=pair_key)

    bit = {s: None for s in symbols}

    for (a, b), cnt in items:
        ba = bit[a]
        bb = bit[b]
        if ba is None and bb is None:
            bit[a] = 0
            bit[b] = 1
        elif ba is None and bb is not None:
            if bb == 1:
                bit[a] = 0
        elif ba is not None and bb is None:
            if ba == 0:
                bit[b] = 1

    for s in symbols:
        if bit[s] is None:
            bit[s] = 0

    return bit


def compress_recompression_greedy(text):
    """
    Recompression-style RLSLP with deterministic greedy pair partition.
    """
    slp = SLP()
    seq = [slp.get_preterminal(ch) for ch in text]

    while len(seq) > 1:
        changed = False

        # block compression (runs)
        new_seq = []
        i = 0
        n = len(seq)
        while i < n:
            j = i + 1
            while j < n and seq[j] == seq[i]:
                j += 1
            run_len = j - i
            if run_len >= 2:
                base = seq[i]
                nt = slp.new_nonterminal()
                slp.set_rule_run(nt, base, run_len)
                new_seq.append(nt)
                changed = True
            else:
                new_seq.append(seq[i])
            i = j
        seq = new_seq

        if len(seq) <= 1:
            break

        # pair compression with greedy partition
        bits = _compute_greedy_bits_for_sequence(seq)
        new_seq = []
        pair_nt = {}
        i = 0
        n = len(seq)
        while i < n:
            if i < n - 1:
                a_sym = seq[i]
                b_sym = seq[i + 1]
                if bits[a_sym] == 0 and bits[b_sym] == 1:
                    pair = (a_sym, b_sym)
                    if pair in pair_nt:
                        nt = pair_nt[pair]
                    else:
                        nt = slp.new_nonterminal()
                        slp.set_rule_binary(nt, a_sym, b_sym)
                        pair_nt[pair] = nt
                    new_seq.append(nt)
                    changed = True
                    i += 2
                    continue
            new_seq.append(seq[i])
            i += 1
        seq = new_seq

        # fallback if nothing changed
        if not changed:
            if len(seq) <= 1:
                break
            new_seq = []
            pair_nt = {}
            i = 0
            n = len(seq)
            while i < n:
                if i < n - 1:
                    a_sym = seq[i]
                    b_sym = seq[i + 1]
                    pair = (a_sym, b_sym)
                    if pair in pair_nt:
                        nt = pair_nt[pair]
                    else:
                        nt = slp.new_nonterminal()
                        slp.set_rule_binary(nt, a_sym, b_sym)
                        pair_nt[pair] = nt
                    new_seq.append(nt)
                    i += 2
                else:
                    new_seq.append(seq[i])
                    i += 1
            seq = new_seq

    if len(seq) == 1:
        slp.start = seq[0]
    else:
        slp.start = binary_tree_from_sequence(slp, seq)

    return slp