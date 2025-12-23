from slp import SLP
from utils import binary_tree_from_sequence

def compress_sequitur(text):
    """
    Sequitur-inspired offline grammar:
      - repeatedly finds a digram that appears at least twice,
      - introduces / reuses a rule for that digram,
      - replaces all non-overlapping occurrences by the rule.
    Non-start rules are always of length 2; start is converted to CNF.
    """
    slp = SLP()
    start_seq = [slp.get_preterminal(ch) for ch in text]

    # Use 0 as a special key representing the start sequence (not a real nonterminal)
    START_KEY = 0
    rules = {START_KEY: list(start_seq)}  # key -> list of SLP nonterminals

    while True:
        # build mapping digram -> list of (rule_key, index)
        digram_positions = {}
        for rname, rhs in rules.items():
            length = len(rhs)
            for i in range(length - 1):
                digram = (rhs[i], rhs[i + 1])
                digram_positions.setdefault(digram, []).append((rname, i))

        chosen_digram = None
        for digram, positions in digram_positions.items():
            if len(positions) >= 2:
                chosen_digram = digram
                break

        if chosen_digram is None:
            break

        a_sym, b_sym = chosen_digram

        # check if there is already a rule with exactly this RHS
        reuse_nt = None
        for key, rhs in rules.items():
            if key == START_KEY:
                continue
            if len(rhs) == 2 and rhs[0] == a_sym and rhs[1] == b_sym:
                reuse_nt = key
                break

        if reuse_nt is None:
            reuse_nt = slp.new_nonterminal()
            rules[reuse_nt] = [a_sym, b_sym]
            slp.set_rule_binary(reuse_nt, a_sym, b_sym)

        # replace all occurrences of chosen_digram in all rules except its own
        for rname, rhs in list(rules.items()):
            if rname == reuse_nt:
                continue
            length = len(rhs)
            i = 0
            new_rhs = []
            while i < length:
                if i < length - 1 and rhs[i] == a_sym and rhs[i + 1] == b_sym:
                    new_rhs.append(reuse_nt)
                    i += 2
                else:
                    new_rhs.append(rhs[i])
                    i += 1
            rules[rname] = new_rhs

    final_seq = rules[START_KEY]
    if len(final_seq) == 0:
        slp.start = 0
    elif len(final_seq) == 1:
        slp.start = final_seq[0]
    else:
        slp.start = binary_tree_from_sequence(slp, final_seq)

    return slp