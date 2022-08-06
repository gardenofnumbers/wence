from wither import witherParser, WitherInterpreter
import json
import sys

if len(sys.argv) < 3:
    print(f"Proper usage: {sys.argv[0]} <wither machine> <source>")
    exit(0);

with open(sys.argv[1], 'r') as f:
    p = witherParser(f.read())
    i = WitherInterpreter(p.states)
with open(sys.argv[2], 'r') as f:
    src = f.read();

print(src)
print(json.dumps(p.states))
print()
print()
print()
import code; code.interact(local=locals());
tree = i.run(src)

print("finished!?")
print()
print(json.dumps(tree))