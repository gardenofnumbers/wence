import json
from WenceCompilerPass0 import WenceCompilerPass0
DEBUG_WALKER = False

class WenceWalker(object):
   

    def __init__(self, ast):
        self.trace = ""
        self.ast = ast
        
    def walk(self, node, handlers, depth = 0):
        children = [(x, node[x]) for x in node if type(node[x]) == dict and type(x) == int]
        if DEBUG_WALKER:
            print("\t"*depth + f"c: {node['id']} ({len(children)})")
            print("\t"*depth + json.dumps([c[1]['id'] for c in children]))
        self.trace += f" {node['id']}"
        for (idx, child) in children:
            if child['id'] in handlers:
                if not handlers[child['id']](child, node, idx):
                    continue
            self.walk(child, handlers, depth+1)


class WenceCompiler(object):
    def __init__(self, ast):
        self.ast = ast
        self.walker = WenceWalker(ast);

    def compile(self):
        p0 = WenceCompilerPass0(self.ast, self.walker);
        ast = p0.compile()
        