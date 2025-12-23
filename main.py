from slp import SLP
from jez import compress_recompression, compress_recompression_greedy
from repair import compress_repair
from sequitur import compress_sequitur
from tests import repair_adversary
from balancing import balance

def test(s):
    # print("Testing on:", s)
    compressors = [
        ("RePair", compress_repair),
        ("Sequitur", compress_sequitur),
        ("RecompGreedy", compress_recompression_greedy),
        ("RecompRand", compress_recompression),
        ("RePairBalanced", lambda s: balance(compress_repair(s))),
        ("SequiturBalanced", lambda s: balance(compress_sequitur(s))),
    ]
    for name, func in compressors:
        G = func(s)
        for i in range(len(s)):
            assert G.access(i) == s[i], (f"{name} mismatch at {i}: {G.access(i)!r} vs {s[i]!r}")
        print(f'length: {G.length()}    size: {G.size()}    depth: {G.depth()}  ({name})')
        
    print("OK\n")
    
def get_samples():
    sizes = []
    depths = []
    for n in range(3, 201):
        s = repair_adversary(n, random_extension_side=True, random_block_order=True)
        G = compress_sequitur(s)
        balance(G)
        size = G.size()
        depth = G.depth()
        print(f'n={n} size={size} depth={depth}')
        sizes.append(size)
        depths.append(depth)
    print(sizes)
    print(depths)

# if __name__ == "__main__":
    # test(repair_adversary(200, random_extension_side=True, random_block_order=True))
    # get_samples()
    # s = repair_adversary(200)
    # G = compress_sequitur(s)
    # balance(G)
    # for i in range(len(s)):
    #     assert G.access(i) == s[i], (f"mismatch at {i}: {G.access(i)!r} vs {s[i]!r}")
    # print(f'length: {G.length()}    size: {G.size()}    depth: {G.depth()}')