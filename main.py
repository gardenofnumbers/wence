from wither import witherParser, WitherInterpreter, WenceCompiler

import json
import sys

DEBUG_WITHER = True
if len(sys.argv) < 3:
    print(f"Proper usage: {sys.argv[0]} <wither machine> <source> <?dot output file>")
    exit(0);

with open(sys.argv[1], 'r') as f:
    p = witherParser(f.read())
    i = WitherInterpreter(p.states, p.hdr)
with open(sys.argv[2], 'r') as f:
    src = f.read();



tree = i.run(src)

if DEBUG_WITHER:
    print(json.dumps(tree))

dot, blocks = WenceCompiler(tree).compile(); 


print()
print()
print(json.dumps(blocks))

if len(sys.argv) >= 4:
    with open(sys.argv[3], "w") as f:
        f.write(dot)
else:
    print(dot)



