import random

def repair_adversary(n, random_extension_side=False, random_block_order=False, seed=0):
    random.seed(seed)
    blocks = [[]]
    for i in range(1, n + 1):
        blocks.append(blocks[-1])
        if random_extension_side and random.choice(['L', 'R']) == 'L':
            blocks[-1] = [i] + blocks[-1]
        else:
            blocks[-1] = blocks[-1] + [i]
    blocks[-1] = blocks[-2] # two last blocks can be the same 
    blocks = blocks[2:] # we care about blocks of length ≥ 2
    if random_block_order:
        random.shuffle(blocks)
    return sum(blocks, [])