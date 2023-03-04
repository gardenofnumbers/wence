from wither import witherParser, WitherInterpreter, WenceCompiler

import json
import sys

if len(sys.argv) < 3:
    print(f"Proper usage: {sys.argv[0]} <wither machine> <source>")
    exit(0);

with open(sys.argv[1], 'r') as f:
    p = witherParser(f.read())
    i = WitherInterpreter(p.states, p.hdr)
with open(sys.argv[2], 'r') as f:
    src = f.read();

tree = i.run(src)

print("finished!?")


c = WenceCompiler(tree); 
c.compile()
print()
print()
print(json.dumps(tree))
